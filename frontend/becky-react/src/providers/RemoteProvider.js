import React from 'react';
import TextField from '@material-ui/core/TextField';



class RemoteProvider extends React.Component {
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
                    <TextField style={{'width': '100%'}} id="remote_addr" label="Remote server IP:" defaultValue={this.props.defaultSettings.remote_addr} onChange={this.handleTextFieldChange} />                
                    <TextField style={{'width': '100%'}} id="remote_path" label="Remote server path:" defaultValue={this.props.defaultSettings.remote_path} onChange={this.handleTextFieldChange} />                
                    <TextField style={{'width': '100%'}} id="ssh_id_path" label="SSH Identity file path:" defaultValue={this.props.defaultSettings.ssh_id_path} onChange={this.handleTextFieldChange} />                
                </form>
            </div>
        );
    }
}

export default RemoteProvider;
