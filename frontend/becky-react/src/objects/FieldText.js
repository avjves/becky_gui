import React from 'react';

class FieldText extends React.Component {

    render() {
        return (
            <div className="row">
                <div className="col-3">
                    {this.props.field}:
                </div>
                <div className="col-9">
                    {this.props.text}
                </div>
            </div>
        );
    }
}

export default FieldText;
