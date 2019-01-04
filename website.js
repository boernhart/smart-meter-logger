/** @jsx React.DOM */

var State = React.createClass({
  refreshData : function(){
  $.ajax({
      url: '/state',
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error("/state", status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data:[]};
  },
  componentDidMount: function() {
    this.interval = setInterval(this.refreshData, 500);
  },
  componentWillUnmount: function() {
    clearInterval(this.interval);
  },
  render: function() {
    return (
    	    <div>
			<h3>Electricity meter reading: {this.state.data.e_sum} kWh</h3>
			<h3>Overall Consumption: {this.state.data.p_sum} W</h3>
			<h3>Power Consumption Phase 1: {this.state.data.p_L1} W</h3>
			<h3>Power Consumption Phase 2: {this.state.data.p_L2} W</h3>
			<h3>Power Consumption Phase 3: {this.state.data.p_L3} W</h3>
    	    </div>
    );
  }
});

React.renderComponent(<State />, $("#state")[0]);
