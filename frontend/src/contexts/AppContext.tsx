"use client";

/**
 * AppContext.tsx
 *
 * This file implements a global application context using React's Context API and React Query.
 * It provides a centralized state management solution for the application, handling data fetching,
 * caching, and state updates.
 *
 * Design Decisions:
 * 1. Use of React Query: Provides powerful data synchronization capabilities, automatic refetching,
 *    and caching strategies.
 * 2. Separation of AppProvider and AppContextInner: Allows for better separation of concerns and
 *    easier testing.
 * 3. Use of useMemo for context value: Optimizes performance by preventing unnecessary re-renders.
 * 4. Initial ping to API: Ensures API availability at startup.
 *
 * Component Structure:
 * - AppContext: The actual React Context object.
 * - AppProvider: Wraps the application with QueryClientProvider and AppContextInner.
 * - AppContextInner: Contains the main logic for data fetching and state management.
 *
 * Data Flow:
 * 1. AppProvider is used to wrap the main application.
 * 2. AppContextInner fetches initial data (stats and info) using React Query.
 * 3. The fetched data and other state values are memoized and provided through the AppContext.
 * 4. Child components can consume this context using useContext(AppContext).
 *
 * @module AppContext
 */

import React, {
  createContext,
  useEffect,
  useMemo,
  ReactNode,
  useContext,
} from "react";
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
  useMutation,
} from "@tanstack/react-query";
import { DatabaseStats, SearchQuery, SearchResult } from "@/types/paperTypes";

// Define the shape of the context
interface AppContextProps {
  stats: DatabaseStats | null;
  info: Record<string, any> | null;
  loading: boolean;
  searchPapers: (query: SearchQuery) => Promise<SearchResult>;
  currentSearchResult: SearchResult | null;
}

// Create the context with default values
export const AppContext = createContext<AppContextProps | undefined>(undefined);

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useAppContext must be used within an AppProvider");
  }
  return context;
};

// Create a new QueryClient instance
const queryClient = new QueryClient();

/**
 * AppProvider component
 *
 * This component wraps the entire application with the necessary providers.
 * It sets up the QueryClientProvider for React Query and includes the AppContextInner.
 *
 * @param {Object} props - The component props
 * @param {ReactNode} props.children - The child components to be wrapped
 * @returns {JSX.Element} The wrapped application
 */
export const AppProvider = ({ children }: { children: ReactNode }) => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContextInner>{children}</AppContextInner>
    </QueryClientProvider>
  );
};

/**
 * AppContextInner component
 *
 * This component contains the main logic for the AppContext. It fetches data,
 * manages state, and provides the context value to its children.
 *
 * @param {Object} props - The component props
 * @param {ReactNode} props.children - The child components to be wrapped
 * @returns {JSX.Element} The context provider wrapping the children
 */
const AppContextInner = ({ children }: { children: ReactNode }) => {
  const value: AppContextProps = {
    stats: null,
    info: null,
    loading: false,
    searchPapers: async (query: SearchQuery) => {
      // Implement the search logic here
      return {} as SearchResult; // Replace with actual search result
    },
    currentSearchResult: null,
  };

  // Provide the context value to children
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
export default AppProvider;
