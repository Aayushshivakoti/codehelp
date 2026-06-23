import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

export class PDFExporter {
  constructor() {
    this.doc = new jsPDF();
  }

  exportUserPerformance(userData, attempts, isAdmin = false) {
    this.doc = new jsPDF();

    // Header
    this.doc.setFontSize(20);
    this.doc.setTextColor(59, 130, 246);
    this.doc.text("Quiz Performance Report", 20, 20);

    // User info
    this.doc.setFontSize(12);
    this.doc.setTextColor(0, 0, 0);
    this.doc.text(`User: ${userData.username}`, 20, 35);
    this.doc.text(`Email: ${userData.email}`, 20, 45);
    this.doc.text(
      `Report Generated: ${new Date().toLocaleDateString()}`,
      20,
      55
    );

    // Summary statistics
    const totalAttempts = attempts.length;
    const averageScore =
      totalAttempts > 0
        ? (
            attempts.reduce((sum, attempt) => sum + attempt.percentage, 0) /
            totalAttempts
          ).toFixed(1)
        : 0;
    const bestScore =
      totalAttempts > 0
        ? Math.max(...attempts.map((attempt) => attempt.percentage)).toFixed(1)
        : 0;

    this.doc.setFontSize(14);
    this.doc.setTextColor(31, 41, 55);
    this.doc.text("Performance Summary", 20, 75);

    this.doc.setFontSize(12);
    this.doc.text(`Total Attempts: ${totalAttempts}`, 20, 90);
    this.doc.text(`Average Score: ${averageScore}%`, 20, 100);
    this.doc.text(`Best Score: ${bestScore}%`, 20, 110);

    // Quiz attempts table
    if (attempts.length > 0) {
      const tableData = attempts.map((attempt) => [
        attempt.quiz_title,
        `${attempt.score}/${attempt.total_questions}`,
        `${attempt.percentage.toFixed(1)}%`,
        this.formatTime(attempt.time_taken),
        new Date(attempt.completed_at).toLocaleDateString(),
      ]);

      autoTable(this.doc, {
        head: [["Quiz Title", "Score", "Percentage", "Time Taken", "Date"]],
        body: tableData,
        startY: 125,
        theme: "grid",
        headStyles: {
          fillColor: [59, 130, 246],
          textColor: [255, 255, 255],
          fontStyle: "bold",
        },
        alternateRowStyles: {
          fillColor: [248, 250, 252],
        },
      });
    }

    // Save the PDF
    const filename = isAdmin
      ? `${userData.username}_performance_report.pdf`
      : "my_quiz_performance.pdf";
    this.doc.save(filename);
  }

  exportQuizReport(quizData, attempts) {
    this.doc = new jsPDF();

    // Header
    this.doc.setFontSize(20);
    this.doc.setTextColor(59, 130, 246);
    this.doc.text("Quiz Report", 20, 20);

    // Quiz info
    this.doc.setFontSize(12);
    this.doc.setTextColor(0, 0, 0);
    this.doc.text(`Quiz: ${quizData.title}`, 20, 35);
    this.doc.text(
      `Description: ${quizData.description || "No description"}`,
      20,
      45
    );
    this.doc.text(
      `Report Generated: ${new Date().toLocaleDateString()}`,
      20,
      55
    );

    // Statistics
    const totalAttempts = attempts.length;
    const averageScore =
      totalAttempts > 0
        ? (
            attempts.reduce((sum, attempt) => sum + attempt.percentage, 0) /
            totalAttempts
          ).toFixed(1)
        : 0;
    const passRate =
      totalAttempts > 0
        ? (
            (attempts.filter((attempt) => attempt.percentage >= 60).length /
              totalAttempts) *
            100
          ).toFixed(1)
        : 0;

    this.doc.setFontSize(14);
    this.doc.setTextColor(31, 41, 55);
    this.doc.text("Quiz Statistics", 20, 75);

    this.doc.setFontSize(12);
    this.doc.text(`Total Attempts: ${totalAttempts}`, 20, 90);
    this.doc.text(`Average Score: ${averageScore}%`, 20, 100);
    this.doc.text(`Pass Rate (≥60%): ${passRate}%`, 20, 110);

    // Attempts table
    if (attempts.length > 0) {
      const tableData = attempts.map((attempt) => [
        attempt.username || "Unknown User",
        `${attempt.score}/${attempt.total_questions}`,
        `${attempt.percentage.toFixed(1)}%`,
        this.formatTime(attempt.time_taken),
        new Date(attempt.completed_at).toLocaleDateString(),
      ]);

      autoTable(this.doc, {
        head: [["User", "Score", "Percentage", "Time Taken", "Date"]],
        body: tableData,
        startY: 125,
        theme: "grid",
        headStyles: {
          fillColor: [59, 130, 246],
          textColor: [255, 255, 255],
          fontStyle: "bold",
        },
        alternateRowStyles: {
          fillColor: [248, 250, 252],
        },
      });
    }

    this.doc.save(`${quizData.title.replace(/[^a-z0-9]/gi, "_")}_report.pdf`);
  }

  exportAllUsersReport(usersData) {
    this.doc = new jsPDF();

    // Header
    this.doc.setFontSize(20);
    this.doc.setTextColor(59, 130, 246);
    this.doc.text("All Users Performance Report", 20, 20);

    this.doc.setFontSize(12);
    this.doc.setTextColor(0, 0, 0);
    this.doc.text(
      `Report Generated: ${new Date().toLocaleDateString()}`,
      20,
      35
    );
    this.doc.text(`Total Users: ${usersData.length}`, 20, 45);

    // Users table
    if (usersData.length > 0) {
      const tableData = usersData.map((user) => [
        user.username,
        user.email,
        user.attempts || 0,
        user.avg_score ? `${user.avg_score.toFixed(1)}%` : "0%",
        user.best_score ? `${user.best_score.toFixed(1)}%` : "0%",
      ]);

      autoTable(this.doc, {
        head: [["Username", "Email", "Attempts", "Avg Score", "Best Score"]],
        body: tableData,
        startY: 60,
        theme: "grid",
        headStyles: {
          fillColor: [59, 130, 246],
          textColor: [255, 255, 255],
          fontStyle: "bold",
        },
        alternateRowStyles: {
          fillColor: [248, 250, 252],
        },
      });
    }

    this.doc.save("all_users_performance_report.pdf");
  }

  formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  }
}

export default PDFExporter;
