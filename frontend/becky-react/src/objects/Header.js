import React from 'react';

class Header extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        if(this.props.size == 'h1' || !this.props.size) {
            return (
                <h1>{this.props.text}</h1>
            );
        }
        else if(this.props.size == 'h2') {
            return (
                <h2>{this.props.text}</h2>
            );
        }
        else if(this.props.size == 'h3') {
            return (
                <h3>{this.props.text}</h3>
            );
        }
    }
}

export default Header;
