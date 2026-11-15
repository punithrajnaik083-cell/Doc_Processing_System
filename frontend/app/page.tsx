"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface HealthResponse {
  status: string;
  version: string;
}

export default function DashboardPage() {
  const { data, isError, isLoading, error } = useQuery<HealthResponse>({
    queryKey: ["health"],
    queryFn: () => apiFetch<HealthResponse>("/api/health"),
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Monitor and process documents with automatic validation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isLoading ? (
            <Badge variant="outline" className="text-slate-500">
              Checking API...
            </Badge>
          ) : isError ? (
            <Badge variant="destructive" className="bg-red-600 text-white hover:bg-red-700">
              API not reachable
            </Badge>
          ) : (
            <Badge variant="success" className="bg-emerald-600 text-white hover:bg-emerald-700">
              API connected
            </Badge>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <span className="font-medium text-slate-700">Backend API:</span>
              {isLoading ? (
                <span className="text-slate-500">Connecting...</span>
              ) : isError ? (
                <span className="text-red-600 font-semibold">
                  Unreachable ({error?.message || "Failed to fetch"})
                </span>
              ) : (
                <span className="text-emerald-700 font-semibold">
                  Connected (v{data?.version || "0.1.0"})
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Connected endpoint: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/health
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

