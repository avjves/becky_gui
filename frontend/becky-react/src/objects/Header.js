import React from 'react';

class Header extends React.Component {

    constructor(props) {
        super(props);
    }


    getText() {
        if(this.props.children) {
            return this.props.children;
        }
        else {
            return this.props.text;
        }
    }

    render() {
        var textToShow = this.getText()
        if(this.props.size == 'h1' || !this.props.size) {
            return (
                <h1>{textToShow}</h1>
            );
        }
        else if(this.props.size == 'h2') {
            return (
                <h2>{textToShow}</h2>
            );
        }
        else if(this.props.size == 'h3') {
            return (
                <h3>{textToShow}</h3>
            );
        }
        else if(this.props.size == 'h4') {
            return (
                <h4>{textToShow}</h4>
            );
        }
        else if(this.props.size == 'h5') {
            return (
                <h5>{textToShow}</h5>
            );
        }
    }
}

export default Header;
