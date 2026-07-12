import { Link } from "react-router";
import styles from "./Header.module.css";

export default function Header() {
    return (
        <header className={styles.header}>
            <nav className={styles.nav}>
                <Link to="/" className={styles.brand}>
                    BSCPE
                </Link>

                <div className={styles.primaryLinks}>
                    <Link to="/chat" className={styles.navLink}>Chat</Link>
                    <Link to="/history" className={styles.navLink}>History</Link>
                    <Link to="/about" className={styles.navLink}>About</Link>
                </div>

                {/* <div className={styles.authLinks}>
                    <Link to="/register" className={styles.navLink}>Register</Link>
                    <Link to="/login" className={styles.loginLink}>Login</Link>
                </div> */}
            </nav>
        </header>
    );
}