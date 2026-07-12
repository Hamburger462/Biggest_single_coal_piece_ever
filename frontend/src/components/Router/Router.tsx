import { Routes, Route } from "react-router";
import styles from "./Router.module.css";

import HomePage from "../../pages/HomePage";
import ChatPage from "../../pages/ChatPage/ChatPage";
import HistoryPage from "../../pages/HistoryPage/HistoryPage";
// import RegisterPage from "../../pages/RegisterPage";
// import LoginPage from "../../pages/LoginPage";

export default function Router() {
    return (
        <main className={styles.main}>
            <section className={styles.section}>
                <Routes>
                    <Route path="/" element={<HomePage />} />

                    <Route path="/chat" element={<ChatPage />} />

                    <Route path="/history" element={<HistoryPage />} />

                    {/* <Route path="/register" element={<RegisterPage />} />
                    <Route path="/login" element={<LoginPage />} /> */}
                </Routes>
            </section>
        </main>
    );
}
