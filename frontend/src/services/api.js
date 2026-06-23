import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem("userRole");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default {
  // Auth endpoints
  login: (credentials) => api.post("/login", credentials),
  register: (userData) => api.post("/register", userData),
  getProfile: () => api.get("/profile"),

  // Subject endpoints
  getSubjects: () => api.get("/subjects"),
  createSubject: (subjectData) => api.post("/subjects", subjectData),
  deleteSubject: (subjectId) => api.delete(`/subjects/${subjectId}`),

  // Chapter endpoints
  getChapters: (subjectId) => api.get(`/subjects/${subjectId}/chapters`),
  createChapter: (chapterData) => api.post("/chapters", chapterData),
  updateChapter: (chapterId, data) => api.put(`/chapters/${chapterId}`, data),
  deleteChapter: (chapterId) => api.delete(`/chapters/${chapterId}`),

  // Quiz endpoints
  getQuizzes: (chapterId) => api.get(`/chapters/${chapterId}/quizzes`),
  createQuiz: (quizData) => api.post("/quizzes", quizData),
  updateQuiz: (quizId, quizData) => api.put(`/quizzes/${quizId}`, quizData),
  deleteQuiz: (quizId) => api.delete(`/quizzes/${quizId}`),
  getQuizQuestions: (quizId, params) => api.get(`/quizzes/${quizId}/questions`, { params }),
  addQuestion: (quizId, questionData) =>
    api.post(`/quizzes/${quizId}/questions`, questionData),
  updateQuestion: (questionId, questionData) =>
    api.put(`/questions/${questionId}`, questionData),
  deleteQuestion: (questionId) => api.delete(`/questions/${questionId}`),
  startQuiz: (quizId, data) => api.post(`/quizzes/${quizId}/start`, data || {}),
  submitQuiz: (attemptId, submissionData) =>
    api.post(`/attempts/${attemptId}/submit`, submissionData),
  getQuizAttempts: (quizId) => api.get(`/quizzes/${quizId}/attempts`),
  getLockoutStatus: () => api.get("/quizzes/lockout-status"),
  abandonQuiz: (attemptId) => api.post(`/attempts/${attemptId}/abandon`),

  // Code Challenge endpoints
  getChapterChallenges: (chapterId) => api.get(`/chapters/${chapterId}/challenges`),
  getAllChallenges: () => api.get('/challenges/all'),
  getChallenge: (challengeId) => api.get(`/challenges/${challengeId}`),
  createChallenge: (challengeData) => api.post('/challenges', challengeData),
  updateChallenge: (challengeId, challengeData) => api.put(`/challenges/${challengeId}`, challengeData),
  deleteChallenge: (challengeId) => api.delete(`/challenges/${challengeId}`),
  toggleChallenge: (challengeId) => api.post(`/challenges/${challengeId}/toggle`),
  addTestCase: (challengeId, testCaseData) => api.post(`/challenges/${challengeId}/testcases`, testCaseData),
  syncTestCases: (challengeId, testCases) => api.put(`/challenges/${challengeId}/testcases`, testCases),
  bulkAddTestCases: (challengeId, bulkData) => api.post(`/challenges/${challengeId}/testcases/bulk`, bulkData),
  testSolution: (challengeId, testData) => api.post(`/challenges/${challengeId}/test-solution`, testData),
  runCode: (codeData) => api.post('/code/run', codeData),
  submitCode: (submissionData) => api.post('/code/submit', submissionData),
  getUserSubmissions: () => api.get('/user/submissions'),

  // User endpoints
  getUserAttempts: (username) => api.get("/user/attempts", { params: username ? { username } : {} }),
  getUserAnalytics: (username) => api.get("/user/analytics", { params: username ? { username } : {} }),
  getRecommendations: () => api.get("/recommendations"),
  getQuizComments: (quizId) => api.get(`/quizzes/${quizId}/comments`),
  addQuizComment: (quizId, commentData) => api.post(`/quizzes/${quizId}/comments`, commentData),
  uploadProfilePic: (formData) => api.post("/profile/upload", formData, { headers: { "Content-Type": "multipart/form-data" } }),
  getDailyChallenge: (subjectId) => api.get(`/subjects/${subjectId}/daily-challenge`),
  searchContent: (query) => api.get("/search", { params: { q: query } }),
  checkPlagiarism: (challengeId) => api.get(`/admin/challenges/${challengeId}/plagiarism`),
  joinMatchmaking: () => api.post("/matchmaking/join"),
  getMatchmakingStatus: () => api.get("/matchmaking/status"),
  getAIHint: (challengeId, data) => api.post(`/challenges/${challengeId}/ai-hint`, data),
  visualizeCode: (codeData) => api.post("/code/visualize", codeData),
  getTournaments: () => api.get("/tournaments"),
  createTournament: (tourData) => api.post("/tournaments", tourData),
  updateTournament: (tourId, tourData) => api.put(`/tournaments/${tourId}`, tourData),
  deleteTournament: (tourId) => api.delete(`/tournaments/${tourId}`),
  registerTournament: (tourId) => api.post(`/tournaments/${tourId}/register`),
  getTournamentLeaderboard: (tourId) => api.get(`/tournaments/${tourId}/leaderboard`),
  getTournamentQuestions: (tourId) => api.get(`/tournaments/${tourId}/questions`),
  addTournamentQuestion: (tourId, data) => api.post(`/tournaments/${tourId}/questions`, data),
  removeTournamentQuestion: (tourId, tQId) => api.delete(`/tournaments/${tourId}/questions/${tQId}`),
  submitTournamentQuizAnswer: (tourId, data) => api.post(`/tournaments/${tourId}/submit-quiz-answer`, data),
  completeTournament: (tourId) => api.post(`/tournaments/${tourId}/complete`),
  createTournamentCustomQuestion: (tourId, data) => api.post(`/tournaments/${tourId}/custom-question`, data),
  getAllQuizQuestions: () => api.get("/admin/questions/all"),
  getCombatStatus: (roomId) => api.get(`/combat/room/${roomId}/status`),
  updateCombatProgress: (roomId, progressData) => api.post(`/combat/room/${roomId}/progress`, progressData),

  // Admin endpoints
  getUsers: () => api.get("/admin/users"),
  addUser: (userData) => api.post("/admin/users", userData),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  updateUser: (userId, userData) => api.put(`/admin/users/${userId}`, userData),
  getReports: () => api.get("/admin/reports"),
  impersonateUser: (userId) => api.post(`/admin/impersonate/${userId}`),

  // Job management endpoints
  testUserReminders: () => api.post("/admin/jobs/test-reminders"),
  testAdminReport: () => api.post("/admin/jobs/test-admin-report"),
  testCleanup: () => api.post("/admin/jobs/test-cleanup"),
  getInactiveUsers: () => api.get("/admin/jobs/inactive-users"),
  getDailyStats: () => api.get("/admin/jobs/daily-stats"),

  // Bookmark and AI Chat gamified endpoints
  toggleBookmark: (data) => api.post("/bookmarks", data),
  getBookmarks: () => api.get("/bookmarks"),
  sendAIChatMessage: (challengeId, chatData) => api.post(`/challenges/${challengeId}/ai-chat`, chatData),
};

