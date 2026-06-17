import dayjs from "dayjs";
import { DeliveryOption } from "./DeliveryOptions";
import axios from "axios";
export function OrderSummary({ deliveryOptions, cart, loadCart }) {
    return (
        <div className="order-summary">

            {deliveryOptions.length > 0 && cart.map((cartItems) => {

                const selectDeliveryOption = deliveryOptions
                    .find((deliveryOption) => {
                        return deliveryOption.id === cartItems.deliveryOptionId;
                    });
                
                    const deleteCartItem = async () => {
                        await axios.delete(`/api/cart-items/${cartItems.productId}`)
                        await loadCart() ;
                    }

                    const updateCartItem = async () => {
                        const newQuantity = prompt('Enter new quantity (1-10):', cartItems.quantity);
                        if (newQuantity && newQuantity > 0 && newQuantity <= 10) {
                            await axios.put(`/api/cart-items/${cartItems.productId}`, { quantity: parseInt(newQuantity) });
                            await loadCart();
                        }
                    }
                return (
                    <div key={cartItems.productId} className="cart-item-container">
                        <div className="delivery-date">
                            Delivery date:{dayjs(selectDeliveryOption.estimatedDeliveryTimeMs).format('dddd,MMMM,D')}
                        </div>

                        <div className="cart-item-details-grid">
                            <img className="product-image"
                                src={cartItems.product.image} />

                            <div className="cart-item-details">
                                <div className="product-name">
                                    {cartItems.product.name}
                                </div>
                                <div className="product-price">
                                    {cartItems.product.priceCents}
                                </div>
                                <div className="product-quantity">
                                    <span>
                                        Quantity: <span className="quantity-label">{cartItems.quantity}</span>
                                    </span>
                                    <span className="update-quantity-link link-primary"
                                        onClick={updateCartItem}>
                                        Update
                                    </span>
                                    <span className="delete-quantity-link link-primary"
                                    onClick={deleteCartItem}>
                                        Delete
                                    </span>
                                </div>
                            </div>

                            <DeliveryOption deliveryOptions={deliveryOptions} cartItems={cartItems}  loadCart={loadCart}/>
                        </div>
                    </div>
                );
            })}

        </div>
    );
}