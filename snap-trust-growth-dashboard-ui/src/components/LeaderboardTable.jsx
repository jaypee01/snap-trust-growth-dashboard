import React from "react";
import { Table, TableHead, TableRow, TableCell, TableBody, Paper } from "@mui/material";

export default function LeaderboardTable({ data, entity }) {
  return (
    <Paper elevation={2} sx={{ mb: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            {entity === "customer" ? (
              <>
                <TableCell>Customer ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Trust Score</TableCell>
                <TableCell>Loyalty Tier</TableCell>
              </>
            ) : (
              <>
                <TableCell>Merchant ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Trust Score</TableCell>
                <TableCell>Loyalty Tier</TableCell>
              </>
            )}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row) => (
            <TableRow key={entity === "customer" ? row.CustomerID : row.MerchantID}>
              <TableCell>{entity === "customer" ? row.CustomerID : row.MerchantID}</TableCell>
              <TableCell>{entity === "customer" ? row.CustomerName : row.MerchantName}</TableCell>
              <TableCell>{row.TrustScore}</TableCell>
              <TableCell>{row.LoyaltyTier}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  );
}