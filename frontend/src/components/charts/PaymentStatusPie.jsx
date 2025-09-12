import React from "react";
import { ResponsivePie } from "@nivo/pie";

const PaymentStatusPie = ({ data = [] }) => {
  const chartData = data.map((d) => ({ id: d.id, label: d.id, value: d.value }));

  return (
    <div style={{ height: 320 }}>
      <ResponsivePie
        data={chartData}
        margin={{ top: 20, right: 20, bottom: 40, left: 20 }}
        innerRadius={0.5}
        padAngle={1}
        cornerRadius={3}
        activeOuterRadiusOffset={8}
        colors={{ scheme: "paired" }}
        arcLabelsSkipAngle={10}
        arcLinkLabelsSkipAngle={10}
        legends={[
          {
            anchor: "bottom",
            direction: "row",
            translateY: 28,
            itemWidth: 100,
            itemHeight: 14,
            itemTextColor: "#555",
            symbolSize: 10,
          },
        ]}
      />
    </div>
  );
};

export default PaymentStatusPie;


