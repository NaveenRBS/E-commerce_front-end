import axios from 'axios';
import { useEffect, useState } from 'react';
import { Header } from '../../components/Header';
import { ProductGrid } from './ProductGrid';
// import { products } from '../../starting-code/data/products';
import './HomePage.css';


export function HomePage({cart, loadCart}) {

    const [products, setProducts] = useState([]);

    useEffect(() => {
        axios.get('/api/products')
            .then((response) => {
                setProducts(response.data);
            });
    }, []);
        
    return (
        <>
            <title> E Commerce </title>
              <Header cart={cart}/>
            <div className="home-page">
                <ProductGrid products={products} loadCart={loadCart} />
            </div>
        </>
    );
} 