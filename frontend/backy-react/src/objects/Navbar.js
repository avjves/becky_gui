import React from "react";
import {  Link } from "react-router-dom";

class Navbar extends React.Component {

    render() {
        return (
                <div className="navbar navbar-expand navbar-dark topbar shadow bg-dark">
                    <span className="navbar-brand">Backy</span>
                    <div className="navbar-nav">
                        <Link to="/" className="nav-item nav-link">Home</Link>
                        <Link to="/backups/list" className="nav-item nav-link">Backups</Link>
                        <Link to="/settings" className="nav-item nav-link">Settings</Link>
                    </div>
                </div>
           
        )
    }
}

export default Navbar;
