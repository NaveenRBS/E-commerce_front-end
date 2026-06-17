import axios from 'axios';
import { useEffect, useState } from 'react';
import { Header } from '../../components/Header';
import { ProductGrid } from './ProductGrid';
// import { products } from '../../starting-code/data/products';
import './HomePage.css';


export function HomePage({cart, loadCart}) {

    const [products, setProducts] = useState([]);
    const [search, setSearch] = useState('');

    useEffect(() => {
        axios.get('/api/products')
            .then((response) => {
                setProducts(response.data);
            });
    }, []);
        
    return (
        <>
            <title> E Commerce </title>
              <Header cart={cart} onSearch={setSearch}/>
            <div className="home-page">
                {
                    // filter products by name using the search term
                }
                <ProductGrid products={products.filter(p => p.name.toLowerCase().includes(search.toLowerCase()))} loadCart={loadCart} />
            </div>
        </>
    );
} 