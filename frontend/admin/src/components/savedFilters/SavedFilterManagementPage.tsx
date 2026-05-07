import { useEffect, useState } from "react";

import { fetchSavedFilterEnvelope, type SavedFilterEnvelope } from "../../api/client";
import { StatePanel } from "../StatePanel";

interface SavedFilterManagementPageProps {
  savedFiltersUrl: string;
}

export function SavedFilterManagementPage({
  savedFiltersUrl,
}: SavedFilterManagementPageProps) {
  const [envelope, setEnvelope] = useState<SavedFilterEnvelope | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetchSavedFilterEnvelope(savedFiltersUrl)
      .then((payload) => {
        if (alive) {
          setEnvelope(payload);
          setError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setError(caught instanceof Error ? caught.message : "Saved filters unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [savedFiltersUrl]);

  if (error) {
    return (
      <StatePanel
        title="Saved filters unavailable"
        summary={error}
        actionHref="/admin/app"
        actionLabel="Back to admin"
      />
    );
  }

  if (!envelope) {
    return (
      <StatePanel
        title="Loading saved filters"
        summary="Checking your authorized filter shortcuts."
      />
    );
  }

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Saved filters</p>
          <h1>{envelope.admin_area.replaceAll("_", " ")}</h1>
        </div>
        <a className="button-link" href={envelope.actions.return_url}>
          Refresh
        </a>
      </div>
      {envelope.saved_filters.length ? (
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Filter</th>
                <th>Summary</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {envelope.saved_filters.map((savedFilter) => (
                <tr key={savedFilter.filter_id}>
                  <td>{savedFilter.display_name}</td>
                  <td>{savedFilter.filter_key}</td>
                  <td>{Object.values(savedFilter.safe_summary).join(", ") || "No criteria"}</td>
                  <td>
                    <a href={savedFilter.restore_href}>Restore</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <StatePanel
          title="No saved filters"
          summary="This scope has no saved filters for the selected admin area."
        />
      )}
    </section>
  );
}
