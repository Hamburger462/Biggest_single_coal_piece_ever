import { useState } from "react";
import type { ChangeEvent } from "react";

import { useModel } from "../../hooks/useModel";
import type { SingleResult, CandidateResult } from "../../hooks/useModel";
import { useHistory } from "../../hooks/useHistory";

import styles from "./ChatPage.module.css";

import addIcon from "../../icons/add.png";

export default function ChatPage() {
    const [image, setImage] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | undefined>();
    const [text, setText] = useState<string>("");
    const [response, setResponse] = useState<
        SingleResult | CandidateResult[] | null
    >(null);

    const { loading, error, predictCandidates, predictSingle } = useModel();
    const { logSingle, logCandidates } = useHistory();

    const canSubmit = Boolean(image) && !loading;

    function handleImageChange(e: ChangeEvent<HTMLInputElement>) {
        if (!e.target.files) {
            return;
        }

        setPreviewUrl(undefined);

        setImage(e.target.files?.[0]);

        const url = URL.createObjectURL(e.target.files[0]);
        setPreviewUrl(url);
    }

    async function makeAPrediction() {
        if (!image) return;

        const result = await predictSingle({ image, user_query: text });
        if (!result) return;

        setResponse(result);

        // Logging is fire-and-forget: a failure here shouldn't block the
        // person from seeing their prediction, so useHistory's own
        // error/loading state is left unused here rather than surfaced
        // in this UI.
        logSingle({ image_name: image.name, user_query: text, result });
    }

    async function makeCandidatesPrediction() {
        if (!image) return;

        const results = await predictCandidates({
            image,
            user_query: text,
            candidates: 5,
        });
        if (!results) return;

        setResponse(results);

        logCandidates({ image_name: image.name, user_query: text, results });
    }

    return (
        <>
            <h1>Chat</h1>

            <div id={styles["Chat-main"]}>
                <form id={styles["Form-main"]} className={styles["Window"]}>
                    <div>
                        <label className={styles["Form-input"]}>
                            {image ? (
                                <img src={previewUrl} id={styles["Form-img"]} />
                            ) : (
                                <>
                                    <img
                                        src={addIcon}
                                        id={styles["Add-icon"]}
                                    />
                                    <div>Add image</div>
                                </>
                            )}
                            <input
                                type="file"
                                accept="image/*"
                                hidden={true}
                                onChange={handleImageChange}
                            />
                        </label>
                    </div>

                    <div>
                        <div
                            contentEditable={true}
                            onChange={(e) => setText(e.target.textContent)}
                            id={styles["Form-text"]}
                        ></div>
                        <div id={styles["Text-hint"]}>Describe the found mineral for more accurate prediction</div>
                    </div>
                </form>

                <div id={styles["Response-main"]} className={styles["Window"]}>
                    <div className={styles["Response-heading"]}>Model prediction:</div>

                    {loading && <div className={styles["Response-loading"]}>Waiting for a response...</div>}

                    {error && <div className={styles["Response-error"]} role="alert">{error}</div>}

                    {!loading && response && (
                        <div>
                            {Array.isArray(response) ? (
                                <ul className={styles["Response-list"]}>
                                    {response.map((r, i) => (
                                        <li key={i} className={styles["Response-item"]}>
                                            <span>{r.mineral_name} ({r.chemical_formula})</span>
                                            <span>{(r.confidence * 100).toFixed(1)}% confidence</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : "raw_output" in response ? (
                                <div className={styles["Response-raw"]}>{response.raw_output}</div>
                            ) : (
                                <div className={styles["Response-result"]}>
                                    {response.mineral_name} (
                                    {response.chemical_formula})
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            <div id={styles["Btn-container"]} className={styles["Window"]}>
                <button
                    type="button"
                    disabled={!canSubmit}
                    className={styles["Form-btn"]}
                    onClick={makeAPrediction}
                >
                    Predict
                </button>
                <button
                    type="button"
                    onClick={makeCandidatesPrediction}
                    disabled={!canSubmit}
                    className={styles["Form-btn"]}
                >
                    Show top candidates
                </button>
            </div>
        </>
    );
}