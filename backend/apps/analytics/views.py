import threading
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Max, Min, Count
from apps.products.models import Product
from apps.products.serializers import ProductListSerializer


class GlobalStatsView(APIView):
    """
    GET /api/analytics/stats/
    Returns price statistics grouped by source.
    Optional: ?query=iphone
    """
    def get(self, request):
        qs = Product.objects.all()

        query = request.query_params.get("query")
        if query:
            qs = qs.filter(query__icontains=query)

        if not qs.exists():
            return Response({"detail": "No products found."}, status=404)

        by_source = list(
            qs.values("source").annotate(
                avg_price=Avg("price_value"),
                min_price=Min("price_value"),
                max_price=Max("price_value"),
                total=Count("id")
            ).order_by("-total")
        )

        # Round values
        for s in by_source:
            s["avg_price"] = round(float(s["avg_price"] or 0), 2)
            s["min_price"] = round(float(s["min_price"] or 0), 2)
            s["max_price"] = round(float(s["max_price"] or 0), 2)

        overall = qs.aggregate(
            avg=Avg("price_value"),
            min=Min("price_value"),
            max=Max("price_value"),
            total=Count("id")
        )

        return Response({
            "total_products": overall["total"],
            "overall": {
                "avg_price": round(float(overall["avg"] or 0), 2),
                "min_price": round(float(overall["min"] or 0), 2),
                "max_price": round(float(overall["max"] or 0), 2),
            },
            "by_source": by_source,
        })


class DistributionView(APIView):
    """
    GET /api/analytics/distribution/
    Returns price distribution as histogram buckets.
    Optional: ?query=iphone&source=Jumia
    """
    def get(self, request):
        qs = Product.objects.all()

        query = request.query_params.get("query")
        source = request.query_params.get("source")
        if query:
            qs = qs.filter(query__icontains=query)
        if source:
            qs = qs.filter(source__iexact=source)

        if not qs.exists():
            return Response({"detail": "No products found."}, status=404)

        prices = list(qs.values_list("price_value", flat=True))

        # Build histogram buckets
        import numpy as np
        prices_arr = np.array([float(p) for p in prices if p and float(p) > 0])

        if len(prices_arr) == 0:
            return Response({"detail": "No valid prices."}, status=404)

        counts, edges = np.histogram(prices_arr, bins=10)
        buckets = [
            {
                "range_min": round(float(edges[i]), 2),
                "range_max": round(float(edges[i + 1]), 2),
                "count": int(counts[i])
            }
            for i in range(len(counts))
        ]

        return Response({
            "total": len(prices_arr),
            "mean": round(float(prices_arr.mean()), 2),
            "median": round(float(np.median(prices_arr)), 2),
            "std": round(float(prices_arr.std()), 2),
            "min": round(float(prices_arr.min()), 2),
            "max": round(float(prices_arr.max()), 2),
            "buckets": buckets,
        })


class AnalyzeView(APIView):
    """
    POST /api/analytics/analyze/
    Body: { "query": "iphone 13" }

    Runs the full data mining pipeline on products matching the query.
    Returns clustering, anomalies, statistics, association rules, PCA.
    """
    def post(self, request):
        query = request.data.get("query", "").strip()
        if not query:
            return Response(
                {"detail": "Provide a 'query' field."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check we have data for this query
        count = Product.objects.filter(query__icontains=query).count()
        if count == 0:
            return Response(
                {"detail": f"No products found for '{query}'. Run the scraper first."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            from data_mining.pipeline import run_pipeline
            report = run_pipeline(query=query, save_report=False)

            if report is None:
                return Response(
                    {"detail": "Pipeline returned no results."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                "query": query,
                "total_products": report.get("total_products", 0),
                "statistics": report.get("statistics", {}),
                "clusters": report.get("clusters", []),
                "anomalies": report.get("anomalies", []),
                "lof_outliers": report.get("lof_outliers", []),
                "association_rules": report.get("association_rules", {}),
                "pca": report.get("pca", []),
            })

        except Exception as e:
            return Response(
                {"detail": f"Pipeline error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ScrapeAndAnalyzeView(APIView):
    """
    POST /api/analytics/scrape-analyze/
    Body: { "query": "iphone 13" }

    Triggers scraping in background thread, then runs pipeline.
    Returns immediately with a status message.
    """
    _running_jobs = {}

    def post(self, request):
        query = request.data.get("query", "").strip()
        if not query:
            return Response(
                {"detail": "Provide a 'query' field."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if query in self.__class__._running_jobs:
            return Response(
                {"detail": f"Scraping already running for '{query}'."},
                status=status.HTTP_409_CONFLICT
            )

        # Run scraping in background thread
        thread = threading.Thread(
            target=self._run_scrape_pipeline,
            args=(query,),
            daemon=True
        )
        self.__class__._running_jobs[query] = "running"
        thread.start()

        return Response({
            "status": "started",
            "message": f"Scraping started for '{query}'. Call GET /api/analytics/job-status/?query={query} to check progress.",
            "query": query,
        }, status=status.HTTP_202_ACCEPTED)

    def _run_scrape_pipeline(self, query):
        try:
            from scraping.runner import run_scraping
            run_scraping(query)
        except Exception as e:
            print(f"[ScrapeAndAnalyze] Scraping error: {e}")
        finally:
            self.__class__._running_jobs.pop(query, None)


class JobStatusView(APIView):
    """
    GET /api/analytics/job-status/?query=iphone
    Check if a scraping job is still running.
    """
    def get(self, request):
        query = request.query_params.get("query", "").strip()
        if not query:
            return Response({"detail": "Provide a 'query' param."}, status=400)

        is_running = query in ScrapeAndAnalyzeView._running_jobs
        count = Product.objects.filter(query__icontains=query).count()

        return Response({
            "query": query,
            "status": "running" if is_running else "idle",
            "products_in_db": count,
        })