import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import './App.css'

// 페이지 컴포넌트 import
import HomePage from './components/HomePage.jsx'
import BookAnalysisPage from './components/BookAnalysisPage.jsx'
import DocumentGenerationPage from './components/DocumentGenerationPage.jsx'
import ResultsPage from './components/ResultsPage.jsx'
import Header from './components/Header.jsx'
import Footer from './components/Footer.jsx'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analyze" element={<BookAnalysisPage />} />
            <Route path="/generate" element={<DocumentGenerationPage />} />
            <Route path="/results/:taskId" element={<ResultsPage />} />
          </Routes>
        </main>
        <Footer />
        <Toaster />
      </div>
    </Router>
  )
}

export default App
