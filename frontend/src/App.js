import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
    const [products, setProducts] = useState([]);

    useEffect(() => {
        // Fetch data from Flask API
        axios.get('http://127.0.0.1:5000/products')
            .then(response => {
                setProducts(response.data); // Set products from API
            })
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    return (
        <div>
            <h1>MarketHub Products</h1>
            <ul>
                {products.map(product => (
                    <li key={product.product_id}>
                        {product.product_name} - ${product.price}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default App;
