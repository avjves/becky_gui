import React from 'react';
import TextField from '@material-ui/core/TextField';



class LocalScanner extends React.Component {
    constructor(props) {
        super(props);
        this.handleTextFieldChange = this.handleTextFieldChange.bind(this);
    }

    onComponentDidMount() {
        this.props.clearParameters();
    }

    handleTextFieldChange(event) {
        this.props.changeScannerParameter(event.target.id, event.target.value);
    }

    render() {
        return (
            <div className="col-11">
                No settings to set.
            </div>
        );
    }
}

export default LocalScanner;
