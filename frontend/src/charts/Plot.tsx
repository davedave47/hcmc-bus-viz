// One Plotly component built from the slim dist bundle (avoids the full plotly.js).
import Plotly from 'plotly.js-dist-min'
import createPlotlyComponent from 'react-plotly.js/factory'

const Plot = createPlotlyComponent(Plotly)
export default Plot
