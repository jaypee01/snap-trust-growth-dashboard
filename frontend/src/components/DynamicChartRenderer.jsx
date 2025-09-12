import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Alert, CircularProgress } from '@mui/material';
import { ResponsiveLine } from '@nivo/line';
import { ResponsiveBar } from '@nivo/bar';
import { ResponsivePie } from '@nivo/pie';

const DynamicChartRenderer = ({ chartCode, data, isLoading }) => {
  const [ChartComponent, setChartComponent] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!chartCode) return;

    try {
      // Create a function that returns the chart component
      const createChartComponent = () => {
        // Extract the chart type from the code
        const chartTypeMatch = chartCode.match(/import.*Responsive(\w+).*from '@nivo\/(\w+)'/);
        if (!chartTypeMatch) {
          throw new Error('Could not determine chart type from code');
        }

        const chartType = chartTypeMatch[1];
        const chartPackage = chartTypeMatch[2];

        // Map chart types to their components (only available packages)
        const chartComponents = {
          'Line': ResponsiveLine,
          'Bar': ResponsiveBar,
          'Pie': ResponsivePie
        };

        const ChartComponent = chartComponents[chartType];
        if (!ChartComponent) {
          throw new Error(`Unsupported chart type: ${chartType}`);
        }

        return ChartComponent;
      };

      const Component = createChartComponent();
      setChartComponent(() => Component);
      setError(null);
    } catch (err) {
      setError(err.message);
      setChartComponent(null);
    }
  }, [chartCode]);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ margin: 2 }}>
        Error rendering chart: {error}
      </Alert>
    );
  }

  if (!ChartComponent || !data) {
    return (
      <Alert severity="info" sx={{ margin: 2 }}>
        No chart data available
      </Alert>
    );
  }

  return (
    <Paper elevation={2} sx={{ padding: 2, margin: 2 }}>
      <Typography variant="h6" gutterBottom>
        Generated Chart
      </Typography>
      <Box sx={{ height: '400px', width: '100%' }}>
        <ChartComponent data={data} />
      </Box>
    </Paper>
  );
};

export default DynamicChartRenderer;
