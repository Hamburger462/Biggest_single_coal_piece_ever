import styles from "./AboutPage.module.css";

export default function AboutPage() {
    return (
        <div id={styles["About-main"]}>
            <div className={styles["Window"]}>
                <h1>About BSCPE</h1>
                <p id={styles["About-intro"]}>
                    BSCPE is a mineral identification tool built by
                    fine-tuning a vision-language model on labeled mineral
                    photographs, so it can look at a photo of a specimen and
                    return a mineral name and chemical formula.
                </p>
            </div>

            <div className={styles["Window"]}>
                <div id={styles["Model-heading"]}>Model</div>
                <p id={styles["Model-text"]}>
                    BSCPE is built on <strong>llava-1.5-7b-hf</strong>, a
                    7-billion-parameter vision-language model, fine-tuned
                    specifically for mineral identification rather than
                    general-purpose image description.
                </p>
            </div>

            <div className={styles["Window"]}>
                <div id={styles["Dataset-heading"]}>Dataset</div>
                <p id={styles["Dataset-text"]}>
                    Training data combines the{" "}
                    <a
                        href="https://www.kaggle.com/datasets/floriangeillon/mineral-photos"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Mineral Photos dataset
                    </a>{" "}
                    on Kaggle with programmatically generated text prompts -
                    each image paired with a varied, naturally-worded
                    question (a plain "what is this?", a geological-log
                    style description, field-note style observations like
                    hardness or luster) and a structured JSON answer giving
                    the mineral name and chemical formula.
                </p>
            </div>

            <div className={styles["Window-important"]}>
                <div id={styles["Limitations-heading"]}>Limitations</div>
                <ul id={styles["Limitations-list"]}>
                    <li>
                        <strong>Only recognizes a fixed set of mineral
                        classes.</strong> The model was fine-tuned on a
                        limited number of mineral types. Shown a specimen
                        outside that set, it will still confidently return
                        one of its known classes rather than say "I don't
                        know" - there's currently no way for it to signal
                        that a specimen doesn't match anything it was
                        trained on.
                    </li>
                    <li>
                        <strong>Confuses visually similar minerals.</strong>{" "}
                        Errors cluster among minerals that genuinely look
                        alike - pale, colorless crystals (like baryte,
                        calcite, and quartz), metallic-lustered minerals
                        (like pyrite and hematite), and other look-alike
                        groups are the most common sources of mistakes.
                    </li>
                    <li>
                        <strong>Trained on a relatively small, curated
                        dataset.</strong> The fine-tuning set is modest in
                        size, and the Kaggle source photos tend to be
                        well-lit, uncluttered specimen shots. Real-world
                        photos taken outdoors, at odd angles, or in poor
                        lighting haven't been specifically tested and may
                        be identified less reliably.
                    </li>
                    <li>
                        <strong>Confidence scores are relative, not
                        calibrated.</strong> When BSCPE shows ranked
                        candidates with percentages, those reflect how
                        likely each known class is compared only to the
                        other known classes - not a rigorously calibrated
                        real-world probability, and not a guarantee that
                        the true answer is even among the options shown.
                    </li>
                    <li>
                        <strong>Occasionally returns malformed output.</strong>{" "}
                        The model doesn't always produce valid, parseable
                        JSON. When that happens, BSCPE shows the raw model
                        output instead of a formatted result.
                    </li>
                    <li>
                        BSCPE is a reference tool, not a substitute for
                        professional geological identification - please
                        don't rely on it alone for decisions where an
                        incorrect identification would matter (e.g. safety
                        or purchasing decisions).
                    </li>
                </ul>
            </div>
        </div>
    );
}