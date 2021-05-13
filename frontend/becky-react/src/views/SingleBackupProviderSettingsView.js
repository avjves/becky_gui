import React from "react";
import InputLabel from '@material-ui/core/InputLabel';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";

import Header from '../objects/Header.js';
import LocalProvider from '../providers/LocalProvider.js';
import RemoteProvider from '../providers/RemoteProvider.js';
import S3Provider from '../providers/S3Provider.js';

class SingleBackupProviderSettingsView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            providerDropdownText: 'Select a provider:',
            provider: this.props.backup.provider,
            providerSettings: this.props.backup.providerSettings,
        }

        this.onClickNextButton = this.onClickNextButton.bind(this);
        this.handleChangeProvider = this.handleChangeProvider.bind(this);
        this.changeProviderSettings = this.changeProviderSettings.bind(this);
        this.clearParameters = this.clearParameters.bind(this);
    }

    changeProviderSettings(key, value) {
        var currentSettings = this.state.providerSettings;
        currentSettings[key] = value
        this.setState({providerSettings: currentSettings});
    }

    clearParameters() {
        this.setState({providerSettings: {}});
    }

    getProviderConfigComponent() {
        var component = '';
        switch(this.state.provider) {
            case 'local+differential':
                component = <LocalProvider changeProviderParameter={this.changeProviderSettings} defaultSettings={this.state.providerSettings}/>;
                break
            case 'remote+differential':
                component = <RemoteProvider changeProviderParameter={this.changeProviderSettings} defaultSettings={this.state.providerSettings}/>;
                break;
            case 's3+differential':
                component = <S3Provider changeProviderParameter={this.changeProviderSettings} defaultSettings={this.state.providerSettings} />;
                break;
            default:
                component = '';
        }
        return component;
    }

    onClickNextButton() {
        this.props.updateBackup({'provider': this.state.provider, 'providerSettings': JSON.stringify(this.state.providerSettings)});
    }

    handleChangeProvider(event) {
        this.setState({provider: event.target.value});
    }
    
    render() {
        var defaultValues = {
            'provider': this.props.backup.provider ? this.props.backup.provider : '',
            'providerSettings': this.props.backup.providerSettings ? this.props.backup.providerSettings : '',
        }
        var providerConfig = this.getProviderConfigComponent();
        return (
            <div>
                <Header text='Provider settings:' />
                <Header text='Select a provider to use for backing up:' size='h3'/>
                <div className="row ml-1">
                    <div className="col-2">
                        <FormControl style={{'width': '100%'}}>
                            <InputLabel htmlFor="age-native-simple">Provider</InputLabel>
                            <Select native value={this.state.provider} onChange={this.handleChangeProvider} inputProps={{name: 'provider'}}>
                                  <option aria-label="None" value="" />
                                  <option value={'local+differential'}>Local</option>
                                  <option value={'remote+differential'}>Remote (Over SSH)</option>
                                  <option value={'s3+differential'}>S3 compatible object storage</option>
                            </Select>
                        </FormControl>
                    </div>
                </div>
                <hr />
                <div className="row ml-5">
                    {providerConfig}
                </div>
                <hr />
                <div className="row ml-auto">
                    <Button variant="contained" color='primary' type="button" onClick={this.onClickNextButton}>
                        Next
                    </Button>
                </div>
            </div>
        );
    }
}

export default SingleBackupProviderSettingsView;
