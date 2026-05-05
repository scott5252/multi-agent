import type { BriefingPreferenceProfile } from "../../api/generated/reactAdminApi";

export function BriefingPreferencePanel({
  profile,
  onSave,
}: {
  profile: BriefingPreferenceProfile | null;
  onSave: () => void;
}) {
  if (!profile) {
    return null;
  }
  return (
    <section aria-labelledby="briefing-preferences-heading" className="channel-section">
      <div className="section-heading-row">
        <h2 id="briefing-preferences-heading">Briefing Preferences</h2>
        <button type="button" onClick={onSave}>
          Save Preferences
        </button>
      </div>
      <dl className="preference-grid">
        <div>
          <dt>Timezone</dt>
          <dd>{profile.timezone}</dd>
        </div>
        <div>
          <dt>Location</dt>
          <dd>{profile.location_summary}</dd>
        </div>
        <div>
          <dt>Topics</dt>
          <dd>{profile.news_topics_summary}</dd>
        </div>
        <div>
          <dt>VIP hints</dt>
          <dd>{profile.vip_sender_summary}</dd>
        </div>
        <div>
          <dt>Workday</dt>
          <dd>{profile.workday_hours}</dd>
        </div>
        <div>
          <dt>Commute</dt>
          <dd>{profile.commute_mode}</dd>
        </div>
        <div>
          <dt>Accounts</dt>
          <dd>{profile.default_account_summary}</dd>
        </div>
        <div>
          <dt>Output</dt>
          <dd>{profile.output_style}</dd>
        </div>
        <div>
          <dt>Scheduled time</dt>
          <dd>{profile.scheduled_time_summary}</dd>
        </div>
      </dl>
      <p>Revision {profile.revision}</p>
    </section>
  );
}
