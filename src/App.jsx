import { HomePage } from './pages/home/HomePage'
import { Routes, Route } from 'react-router'
import { CheckoutPage } from './pages/checkout/CheckoutPage'
import { OrdersPage } from './pages/orders/OrdersPage'

import { useEffect, useState } from 'react'
import axios from 'axios';
import './App.css'
import { Header } from './components/Header'


function App() {

  const [cart, setcart] = useState([]);

    const loadCart = async () => {
      const response = await axios.get('/api/cart-items?expand=product') ;
          setcart(response.data);
    }



  useEffect(() => {
    loadCart() ;
  }, []);

  return (
    <>
      <Routes>
        <Route path="/" element={< HomePage cart={cart} loadCart={loadCart} />} />
        <Route path="checkout" element={< CheckoutPage cart={cart} loadCart={loadCart}/>} />
        <Route path="orders" element={<OrdersPage cart={cart} />} />

      </Routes>
    </>
  )
}

export default App
