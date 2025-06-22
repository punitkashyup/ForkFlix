import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { AppProvider, useApp } from './context/AppContext';
import Navbar from './components/layout/Navbar';
import { LoadingSpinner } from './components/common/Loading';
import ErrorBanner from './components/common/ErrorBanner';
import Home from './pages/Home';
import AddRecipe from './pages/AddRecipe';
import RecipeDetail from './pages/RecipeDetail';
import Categories from './pages/Categories';
import { Profile } from './pages/Profile';
import Login from './pages/Login';
import Signup from './pages/Signup';
import './App.css';

// Animation variants
const pageVariants = {
  initial: {
    opacity: 0,
    x: -20,
    transition: { duration: 0.3 }
  },
  in: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3 }
  },
  out: {
    opacity: 0,
    x: 20,
    transition: { duration: 0.3 }
  }
};

// Animated page wrapper
interface AnimatedPageProps {
  children: React.ReactNode;
}

function AnimatedPage({ children }: AnimatedPageProps) {
  const location = useLocation();
  
  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  
  if (prefersReducedMotion) {
    return <div key={location.pathname}>{children}</div>;
  }

  return (
    <motion.div
      key={location.pathname}
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      className="w-full"
    >
      {children}
    </motion.div>
  );
}

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useApp();

  if (loading.isLoading) {
    return (
      <motion.div 
        className="min-h-screen flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <LoadingSpinner size="large" message="Loading..." />
      </motion.div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <AnimatedPage>{children}</AnimatedPage>;
}

// Public Route Component (redirect to home if logged in)
interface PublicRouteProps {
  children: React.ReactNode;
}

function PublicRoute({ children }: PublicRouteProps) {
  const { user, loading } = useApp();

  if (loading.isLoading) {
    return (
      <motion.div 
        className="min-h-screen flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <LoadingSpinner size="large" message="Loading..." />
      </motion.div>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return <AnimatedPage>{children}</AnimatedPage>;
}

// Animated Routes Component
function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait" initial={false}>
      <Routes location={location} key={location.pathname}>
        {/* Public Routes */}
        <Route path="/login" element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        } />
        <Route path="/signup" element={
          <PublicRoute>
            <Signup />
          </PublicRoute>
        } />
        
        {/* Protected Routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <Home />
          </ProtectedRoute>
        } />
        <Route path="/add-recipe" element={
          <ProtectedRoute>
            <AddRecipe />
          </ProtectedRoute>
        } />
        <Route path="/recipe/:id" element={
          <ProtectedRoute>
            <RecipeDetail />
          </ProtectedRoute>
        } />
        <Route path="/categories" element={
          <ProtectedRoute>
            <Categories />
          </ProtectedRoute>
        } />
        <Route path="/categories/:category" element={
          <ProtectedRoute>
            <Categories />
          </ProtectedRoute>
        } />
        <Route path="/profile" element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        } />
        
        {/* Catch all route */}
        <Route path="*" element={
          <AnimatedPage>
            <div className="text-center py-20">
              <motion.h1 
                className="text-4xl font-bold text-gray-900 mb-4"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.4 }}
              >
                404
              </motion.h1>
              <motion.p 
                className="text-gray-600 mb-8"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.4, delay: 0.1 }}
              >
                Page not found
              </motion.p>
              <Navigate to="/" replace />
            </div>
          </AnimatedPage>
        } />
      </Routes>
    </AnimatePresence>
  );
}

// Main App Layout
function AppLayout() {
  const { loading, error } = useApp();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <Navbar />
      
      {/* Error Banner */}
      <AnimatePresence>
        {error.hasError && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.3 }}
          >
            <ErrorBanner 
              message={error.message || 'An error occurred'} 
              onClose={() => {}} 
            />
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Loading Overlay */}
      <AnimatePresence>
        {loading.isLoading && (
          <motion.div 
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div 
              className="bg-white rounded-lg p-6 shadow-xl"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <LoadingSpinner 
                size="large" 
                message={loading.message || 'Loading...'} 
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <AnimatedRoutes />
      </main>
    </div>
  );
}

// Root App Component
function App() {
  return (
    <AppProvider>
      <Router>
        <AppLayout />
      </Router>
    </AppProvider>
  );
}

export default App;