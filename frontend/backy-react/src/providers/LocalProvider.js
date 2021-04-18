import React from 'react';
import TextField from '@material-ui/core/TextField';



class LocalProvider extends React.Component {
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
                    <TextField style={{'width': '100%'}} id="output_path" label="Output path:" defaultValue={this.props.defaultSettings.output_path} onChange={this.handleTextFieldChange} />                
                </form>
            </div>
        );
    }
}

export default LocalProvider;
