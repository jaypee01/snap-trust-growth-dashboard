import React from "react";
import { ResponsiveLine } from "@nivo/line";

const MonthlyCollectionsLine = ({ series = [] }) => {
  return (
    <div style={{ height: 360 }}>
      <ResponsiveLine
        data={series}
        margin={{ top: 20, right: 24, bottom: 50, left: 48 }}
        xScale={{ type: "point" }}
        yScale={{ type: "linear", min: "auto", max: "auto", stacked: false }}
        axisBottom={{ tickRotation: -45 }}
        axisLeft={{ legend: "Amount", legendOffset: -40, legendPosition: "middle" }}
        colors={{ scheme: "set1" }}
        lineWidth={3}
        pointSize={6}
        useMesh
        legends={[
          {
            anchor: "bottom-right",
            direction: "column",
            translateX: 0,
            translateY: 0,
            itemWidth: 80,
            itemHeight: 16,
            symbolSize: 10,
          },
        ]}
      />
    </div>
  );
};

export default MonthlyCollectionsLine;


