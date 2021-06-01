import React from 'react';
import TextField from '@material-ui/core/TextField';



class S3Provider extends React.Component {
    constructor(props) {
        super(props);
        this.handleTextFieldChange = this.handleTextFieldChange.bind(this);
    }

    onComponentDidMount() {
        this.props.clearParameters();
    }

    handleTextFieldChange(event) {
        this.props.changeProviderParameter(event.target.id, event.target.value);
    }

    render() {
        return (
            <div className="col-11">
                <form>
                    <TextField style={{'width': '100%'}} id="access_key" label="Access key:" defaultValue={this.props.defaultSettings.access_key} onChange={this.handleTextFieldChange} />                
                    <TextField style={{'width': '100%'}} id="secret_key" label="Secret key:" defaultValue={this.props.defaultSettings.security_key} onChange={this.handleTextFieldChange} />                
                    <TextField style={{'width': '100%'}} id="host" label="Host:" defaultValue={this.props.defaultSettings.host} onChange={this.handleTextFieldChange} />                
                    <TextField style={{'width': '100%'}} id="host_bucket" label="Host bucket:" defaultValue={this.props.defaultSettings.host_bucket} onChange={this.handleTextFieldChange} />                
                    <TextField style={{'width': '100%'}} id="bucket_name" label="Bucket name:" defaultValue={this.props.defaultSettings.bucket_name} onChange={this.handleTextFieldChange} />                
                </form>
            </div>
        );
    }
}

export default S3Provider;
