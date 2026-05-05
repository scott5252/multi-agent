import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { fetchCommandSearch } from "../../api/client";
import type {
  ReactAdminCommandSearchResult,
  ReactAdminShellChrome,
} from "../../api/generated/reactAdminApi";
import { TextInput } from "../primitives";

export function CommandMenu({ shell }: { shell: ReactAdminShellChrome }) {
  const [query, setQuery] = useState("");
  const [remoteResults, setRemoteResults] = useState<
    ReactAdminCommandSearchResult[] | null
  >(null);
  const [error, setError] = useState<string | null>(null);

  const localResults = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return shell.command_results.slice(0, 6);
    }
    return shell.command_results
      .filter(
        (result) =>
          result.label.toLowerCase().includes(normalized) ||
          result.group.toLowerCase().includes(normalized) ||
          result.description?.toLowerCase().includes(normalized),
      )
      .slice(0, 6);
  }, [query, shell.command_results]);

  useEffect(() => {
    if (!query.trim()) {
      setRemoteResults(null);
      setError(null);
      return;
    }
    let alive = true;
    fetchCommandSearch(shell.search_url, query)
      .then((payload) => {
        if (alive) {
          setRemoteResults(payload.results);
          setError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setError(caught instanceof Error ? caught.message : "Search unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [query, shell.search_url]);

  const results = remoteResults ?? localResults;

  return (
    <section className="command-menu" aria-label="Command search">
      <label>
        <span className="label">Command</span>
        <span className="search-box">
          <Search aria-hidden="true" size={18} />
          <TextInput
            aria-label="Search authorized admin destinations"
            onChange={(event) => setQuery(event.currentTarget.value)}
            placeholder="Search pages"
            value={query}
          />
        </span>
      </label>
      {error ? <p className="safe-error">{error}</p> : null}
      <div className="command-results">
        {results.length === 0 ? (
          <p>No authorized destinations match this search.</p>
        ) : (
          results.map((result) => (
            <a className="command-result" href={result.href} key={result.result_id}>
              <span>{result.label}</span>
              <small>{result.description ?? result.group}</small>
            </a>
          ))
        )}
      </div>
    </section>
  );
}
