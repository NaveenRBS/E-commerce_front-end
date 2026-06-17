import dayjs from "dayjs";
import axios from "axios";
export function DeliveryOption({ deliveryOptions, cartItems, loadCart }) {
    return (
        <div className="delivery-options">
            <div className="delivery-options-title">
                Choose a delivery option:
            </div>

            {deliveryOptions.map((deliveryOption) => {
                let priceString = 'FREE Shipping';

                if (deliveryOption.priceCents > 0) {
                    priceString = deliveryOption.priceCents + ' - Shipping';
                }

                const updateDeliveryOption = async () => {
                    await axios.put(`/api/cart-items/${cartItems.productId}`,{
                        deliveryOptionId : deliveryOption.id  
                    } );
                    await loadCart() ;
                }
                return (
                    <div key={deliveryOption.id} className="delivery-option" onClick={updateDeliveryOption}>
                        <input type="radio"
                            checked={deliveryOption.id === cartItems.deliveryOptionId}
                            onChange={() => {}}

                            className="delivery-option-input"
                            name={`delivery-option-${cartItems.productId}`} />
                        <div>
                            <div className="delivery-option-date">
                                {dayjs(deliveryOption.estimatedDeliveryTimeMs).format('dddd,MMMM,D')}
                            </div>
                            <div className="delivery-option-price">
                                ₹{priceString}
                            </div>
                        </div>
                    </div>
                );
            })}

        </div>
    );
}