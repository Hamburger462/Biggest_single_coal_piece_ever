import { Link } from "react-router";

import styles from "./HomePage.module.css";

export default function HomePage() {
    return (
        <div id={styles["Home-main"]}>
            <div className={styles["Window"]} id={styles["Hero"]}>
                <h1>Biggest Single Coal Piece Ever</h1>
                <div id={styles["Hero-subtitle"]}>(BSCPE)</div>
                <p id={styles["Hero-description"]}>
                    BSCPE identifies mineral specimens from a photo. Upload a
                    picture, add any field notes you've got, and get back a
                    mineral name and chemical formula in seconds.
                </p>
            </div>

            <div className={styles["Window-important"]}>
                <div id={styles["Problem-heading"]}>What problem is this solving?</div>
                <p id={styles["Problem-text"]}>
                    Identifying a mineral from a photo alone is a hard,
                    fine-grained visual recognition problem - many minerals
                    share color, shape, and luster, and telling them apart
                    often comes down to details a general-purpose model was
                    never trained to notice. BSCPE runs on a vision-language
                    model fine-tuned specifically on labeled mineral
                    photographs, turning that open-ended guess into a
                    structured answer: a specific name and chemical formula,
                    with a ranked list of alternatives when the model isn't
                    fully certain.
                </p>
            </div>

            <div id={styles["Cta-container"]}>
                <Link
                    to="/chat"
                    className={`${styles["Home-btn"]} ${styles["Home-btn-primary"]}`}
                >
                    Start identifying
                </Link>
                <Link to="/history" className={styles["Home-btn"]}>
                    View past identifications
                </Link>
            </div>
        </div>
    );
}