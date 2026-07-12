import { useEffect, useState } from "react";

import { useHistory } from "../../hooks/useHistory";
import type { HistoryEntity } from "../../hooks/useHistory";
import type { CandidateResult } from "../../hooks/useModel";

import styles from "./HistoryPage.module.css";

type ParsedEntry = {
    id: string;
    image: string;
    query: string;
    mineralName?: string;
    chemicalFormula?: string;
    rawAnswer?: string;
    createdAt?: string;
    candidates?: CandidateResult[];
};

// Entities are stored as {conversations: [human, gpt]}, with the gpt turn
// holding the answer as a JSON *string* (see db_handlers.py) - this
// unpacks that back into plain fields for display. Works the same way
// whether the entity came from /log/single or /log/candidates, since
// log_candidate_predictions stores the top-ranked candidate in the same
// {mineral_name, chemical_formula} shape. Entries logged via
// /log/candidates additionally carry the full ranked list under
// entity.candidates - single-prediction entries simply won't have it.
function parseEntity(entity: HistoryEntity): ParsedEntry {
    const humanValue = entity.conversations[0]?.value ?? "";
    const query = humanValue.replace(/^<image>\n/, "").trim();

    const gptValue = entity.conversations[1]?.value ?? "";
    let mineralName: string | undefined;
    let chemicalFormula: string | undefined;
    let rawAnswer: string | undefined;

    try {
        const parsed = JSON.parse(gptValue);
        mineralName = parsed.mineral_name;
        chemicalFormula = parsed.chemical_formula;
    } catch {
        rawAnswer = gptValue;
    }

    return {
        id: entity.id,
        image: entity.image,
        query,
        mineralName,
        chemicalFormula,
        rawAnswer,
        createdAt: entity.created_at,
        candidates: entity.candidates,
    };
}

function formatTimestamp(value?: string): string {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    return date.toLocaleString();
}

export default function HistoryPage() {
    const [entries, setEntries] = useState<ParsedEntry[]>([]);
    const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
    const { loading, error, fetchHistory } = useHistory();

    useEffect(() => {
        load();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    async function load() {
        const data = await fetchHistory();
        if (data) setEntries(data.map(parseEntity));
    }

    function toggleCandidates(id: string) {
        setExpandedIds((prev) => {
            const next = new Set(prev);
            if (next.has(id)) {
                next.delete(id);
            } else {
                next.add(id);
            }
            return next;
        });
    }

    return (
        <>
            <h1>History</h1>

            <div id={styles["History-main"]} className={styles["Window"]}>
                <div id={styles["History-header"]}>
                    <div className={styles["History-heading"]}>Past identifications</div>
                    <button
                        type="button"
                        className={styles["Refresh-btn"]}
                        onClick={load}
                        disabled={loading}
                    >
                        Refresh
                    </button>
                </div>

                {loading && <div className={styles["History-loading"]}>Loading history...</div>}

                {error && <div className={styles["History-error"]} role="alert">{error}</div>}

                {!loading && !error && entries.length === 0 && (
                    <div className={styles["History-empty"]}>No identifications yet.</div>
                )}

                {!loading && entries.length > 0 && (
                    <ul className={styles["History-list"]}>
                        {entries.map((entry) => (
                            <li key={entry.id} className={styles["History-item"]}>
                                <div className={styles["History-item-main"]}>
                                    <span className={styles["History-image"]}>{entry.image}</span>
                                    {entry.mineralName ? (
                                        <span className={styles["History-result"]}>
                                            {entry.mineralName} ({entry.chemicalFormula})
                                        </span>
                                    ) : (
                                        <span className={styles["History-raw"]}>{entry.rawAnswer}</span>
                                    )}
                                </div>

                                {entry.query && (
                                    <div className={styles["History-query"]}>&ldquo;{entry.query}&rdquo;</div>
                                )}

                                {entry.candidates && entry.candidates.length > 0 && (
                                    <div className={styles["Candidates-section"]}>
                                        <button
                                            type="button"
                                            className={styles["Candidates-toggle"]}
                                            onClick={() => toggleCandidates(entry.id)}
                                        >
                                            {expandedIds.has(entry.id)
                                                ? "Hide candidates"
                                                : `Show candidates (${entry.candidates.length})`}
                                        </button>

                                        {expandedIds.has(entry.id) && (
                                            <ul className={styles["Candidates-list"]}>
                                                {entry.candidates.map((c, i) => (
                                                    <li key={i} className={styles["Candidates-item"]}>
                                                        <span>{c.mineral_name} ({c.chemical_formula})</span>
                                                        <span>{(c.confidence * 100).toFixed(1)}%</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        )}
                                    </div>
                                )}

                                <div className={styles["History-time"]}>{formatTimestamp(entry.createdAt)}</div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </>
    );
}