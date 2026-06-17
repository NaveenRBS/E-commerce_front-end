import axios from 'axios';
import { OrderSummary } from './OrderSummary';
import { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import './CheckoutPage.css';
import { PaymentSummary } from './PaymentSymmary';

export function CheckoutPage({ cart, loadCart }) {
    const [deliveryOptions, setDeliveryOptions] = useState([]);
    const [paymentSummary, setPaymentSummary] = useState(null);


    useEffect(() => {
        axios.get('/api/delivery-options?expand=estimatedDeliveryTime')
            .then((response) => {
                setDeliveryOptions(response.data);
            })
    }, []);


    useEffect(() => {
        axios.get('/api/payment-summary')
            .then((response) => {
                setPaymentSummary(response.data);
            })
    }, [cart]);



    return (
        <>
            <title>Checkout</title>

            <Header cart={cart} />

            <div className="checkout-page">
                <div className="page-title">Review your order</div>
                <div className="checkout-grid">

                    <OrderSummary cart={cart} deliveryOptions={deliveryOptions} loadCart={loadCart} />

                    <PaymentSummary paymentSummary={paymentSummary} loadCart={loadCart} />
                </div>
            </div>
        </>
    );
}