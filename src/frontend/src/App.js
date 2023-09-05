import "./App.css";
import { Routes, Route } from "react-router-dom";

import SignUpPage from "./SignUpPage";
import LogInPage from "./LogInPage";
import EditPage from "./EditPage";
import HomePage from "./HomePage";
import SettingPage from "./SettingPage";
import ResetPasswordPage from "./ResetPasswordPage";
import EmailAddressPage from "./EmailAddressPage";
import GoalSurveyPage from "./GoalSurveyPage";
import GoalDetailPage from "./GoalDetailPage";
import ReviewPage from "./ReviewPage";
import HelpPage from "./HelpPage";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<LogInPage />} />
        <Route path="/login" element={<LogInPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/edit" element={<EditPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/settings" element={<SettingPage />} />
        <Route path="/report" element={<GoalSurveyPage />} />
        <Route path="/goals/:goal_id" element={<GoalDetailPage />} />
        <Route path="/review" element={<ReviewPage />} />
        <Route path="/help" element={<HelpPage />} />
      </Routes>
    </>
  );
}

export default App;
