import PropTypes from "prop-types";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import { Link, useLocation, useNavigate } from "react-router";

const navItems = [
  { id: 1, label: "Merchants", link: "/merchants" },
  { id: 2, label: "Consumers", link: "/consumers" },
];

function NavBar() {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogoClick = () => {
    navigate("/");
  };

  const isActive = (itemLink) => {
    return (
      location.pathname === itemLink ||
      location.pathname.startsWith(itemLink + "/")
    );
  };

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <AppBar component="nav">
        <Toolbar>
          <Typography
            variant="h5"
            onClick={handleLogoClick}
            sx={{
              flexGrow: 1,
              display: { xs: "none", sm: "block" },
              cursor: "pointer",
              fontWeight: "bold",
              "&:hover": {
                opacity: 0.8,
              },
            }}
          >
            SnapScore
          </Typography>
          <Box sx={{ display: { xs: "none", sm: "block" } }}>
            {navItems.map((item) => (
              <Link
                key={item.id}
                to={item.link}
                style={{ textDecoration: "none" }}
              >
                <Button
                  sx={{ color: "#fff" }}
                  className={isActive(item.link) ? "active" : ""}
                >
                  {item.label}
                </Button>
              </Link>
            ))}
          </Box>
        </Toolbar>
      </AppBar>
    </Box>
  );
}

NavBar.propTypes = {
  /**
   * Injected by the documentation to work in an iframe.
   * You won't need it on your project.
   */
  window: PropTypes.func,
};

export default NavBar;
