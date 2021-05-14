import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import AboutPage from './AboutPage'
import SearchPage from './SearchPage';
import Menu from './Menu';
import HomePage from './HomePage';
import Footer from './Footer';

const navigation = {
    links: [
        { name: "Home", to: "/home" },
        { name: "Retrieval", to: "/search" },
        { name: "Read me", to: "/about" },
        { name: "Admin", to: "/admin" },
    ]
}


export default class MainPage extends React.Component<{}, {}> {
    render() {
        const { links } = navigation;
        return (<div>
            <Router>
                <div className="App">
                    <div>
                        <Menu links={links} />
                    </div>
                    <Route path="/home" exact component={HomePage} />
                    <Route path="/search" exact component={SearchPage} />
                    <Route path="/about" exact component={AboutPage} />
                    <Footer />
                </div>
            </Router>
        </div>)

    }
}