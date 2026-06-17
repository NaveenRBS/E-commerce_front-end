import './header.css' ;
import { Link } from 'react-router';
import { useState } from 'react';

export function Header ({cart, onSearch}){
    let totalCartQuantity = 0;

    cart.forEach((cartitem) =>{
        totalCartQuantity+= cartitem.quantity;
    });

    const [searchTerm, setSearchTerm] = useState('');

    const handleInputChange = (e) => {
        const v = e.target.value;
        setSearchTerm(v);
        if (!onSearch) return;
        // live-update search results as user types
        onSearch(v);
    }

    const handleButtonClick = () => {
        if (onSearch) onSearch(searchTerm);
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && onSearch) {
            onSearch(searchTerm);
        }
    }

    return(
            <div className="header">
            <div className="left-section">
                <Link to="/" className="header-link">
                    E-COMMERCE
                </Link>
            </div>

            <div className="middle-section">
                <input className="search-bar" type="text" placeholder="Search" value={searchTerm} onChange={handleInputChange} onKeyDown={handleKeyDown} />

                <button className="search-button" onClick={handleButtonClick}>
                    <img className="search-icon" src="images/icons/search-icon.png" />
                </button>
            </div>

            <div className="right-section">
                <Link className="orders-link header-link" to="/orders">

                    <span className="orders-text">Orders</span>
                </Link>

                <Link className="cart-link header-link" to="/checkout">
                    <img className="cart-icon" src="images/icons/cart-icon.png" />
                    <div className="cart-quantity"> {totalCartQuantity} </div>
                    <div className="cart-text">Cart</div>
                </Link>
            </div>
        </div>

    );
}