import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Orders } from './pages/Orders';
import { CreateOrder } from './pages/CreateOrder';
import { OrderDetails } from './pages/OrderDetails';
import { ShippingAddresses } from './pages/ShippingAddresses';
import { CompanyInfo } from './pages/CompanyInfo';
import { Products } from './pages/Products';
import { Users } from './pages/Users';
import { Artworks } from './pages/Artworks';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders"
            element={
              <ProtectedRoute>
                <Layout>
                  <Orders />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <CreateOrder />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders/:orderId"
            element={
              <ProtectedRoute>
                <Layout>
                  <OrderDetails />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/shipping"
            element={
              <ProtectedRoute>
                <Layout>
                  <ShippingAddresses />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/artworks"
            element={
              <ProtectedRoute>
                <Layout>
                  <Artworks />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/company"
            element={
              <ProtectedRoute>
                <Layout>
                  <CompanyInfo />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/products"
            element={
              <ProtectedRoute>
                <Layout>
                  <Products />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute>
                <Layout>
                  <Users />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
