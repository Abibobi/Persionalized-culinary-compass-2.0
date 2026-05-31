import useSWR from "swr";
import api from "./api";
import type {
  MealPlan,
  RankedRecipe,
  SearchResponse,
  UserProfile,
  UserRecipeInteraction,
  RecipeDetail,
  DashboardSummary,
  SearchLogEntry,
} from "./types";

const fetcher = (url: string) => api.get(url).then((res) => res.data);

export function useProfile() {
  return useSWR<UserProfile>("/users/me/profile/", fetcher);
}

export function useDashboard() {
  return useSWR<DashboardSummary>("/users/dashboard/summary/", fetcher);
}

export function useSavedRecipes() {
  return useSWR<UserRecipeInteraction[]>("/recipes/saved/", fetcher);
}

export function useRecentSearches() {
  return useSWR<SearchLogEntry[]>("/search/history/", fetcher);
}

export function useMealPlan(date: string | null) {
  const key = date ? `/meal-plans/${date}/` : null;
  return useSWR<MealPlan>(key, fetcher, {
    shouldRetryOnError: false,
  });
}

export function useRecipeDetail(id: number | null) {
  const key = id ? `/recipes/${id}/` : null;
  return useSWR<RecipeDetail>(key, fetcher);
}

export function useSearch(query: string | null) {
  return useSWR<SearchResponse>(
    query ? ["/search/", query] : null,
    ([url, text]) => api.post(url, { query: text }).then((res) => res.data)
  );
}

export function useRankedRecipes(query: string | null) {
  const { data, error, isLoading, mutate } = useSearch(query);
  return {
    data: data?.results as RankedRecipe[] | undefined,
    aiSuggestions: data?.ai_suggestions ?? null,
    warnings: data?.warnings ?? [],
    normalizedQuery: data?.normalized_query ?? null,
    parsedFilters: data?.parsed_filters ?? null,
    error,
    isLoading,
    mutate,
  };
}
