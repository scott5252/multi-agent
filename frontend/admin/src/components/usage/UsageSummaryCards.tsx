import type { UsageReactSummaryCard } from "../../api/generated/reactAdminApi";

export function UsageSummaryCards({ cards }: { cards: UsageReactSummaryCard[] }) {
  return (
    <section className="usage-card-grid" aria-label="Usage summary">
      {cards.map((card) => (
        <article className={`usage-card usage-card-${card.tone}`} key={card.card_id}>
          <div>
            <p className="eyebrow">{card.label}</p>
            <strong>{card.value}</strong>
            <span>{card.unit}</span>
          </div>
          <p>{card.detail}</p>
          <small className={`usage-status usage-status-${card.status}`}>
            {card.status}
          </small>
        </article>
      ))}
    </section>
  );
}
