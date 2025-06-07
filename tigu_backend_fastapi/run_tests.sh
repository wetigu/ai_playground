#!/bin/bash

# API Test Runner Script
# This script provides different modes for running tests with proper reporting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
COVERAGE=true
VERBOSE=false
PARALLEL=false
FAIL_FAST=false
MARKERS=""
OUTPUT_DIR="test_results"

# Help function
show_help() {
    echo "API Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE          Test type: all, unit, integration, auth, products, orders, companies"
    echo "  -c, --no-coverage        Disable coverage reporting"
    echo "  -v, --verbose            Enable verbose output"
    echo "  -p, --parallel           Run tests in parallel"
    echo "  -f, --fail-fast          Stop on first failure"
    echo "  -m, --markers MARKERS    Run tests with specific markers"
    echo "  -o, --output DIR         Output directory for reports (default: test_results)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                       # Run all tests with coverage"
    echo "  $0 -t auth              # Run only authentication tests"
    echo "  $0 -p -v               # Run tests in parallel with verbose output"
    echo "  $0 -m slow --no-coverage # Run only slow tests without coverage"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -c|--no-coverage)
            COVERAGE=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -f|--fail-fast)
            FAIL_FAST=true
            shift
            ;;
        -m|--markers)
            MARKERS="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            show_help
            exit 1
            ;;
    esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build pytest command
PYTEST_CMD="python -m pytest"

# Add test path based on type
case $TEST_TYPE in
    "all")
        PYTEST_CMD="$PYTEST_CMD tests/"
        ;;
    "unit")
        PYTEST_CMD="$PYTEST_CMD -m unit"
        ;;
    "integration")
        PYTEST_CMD="$PYTEST_CMD -m integration"
        ;;
    "auth")
        PYTEST_CMD="$PYTEST_CMD tests/test_auth.py"
        ;;
    "products")
        PYTEST_CMD="$PYTEST_CMD tests/test_products.py"
        ;;
    "orders")
        PYTEST_CMD="$PYTEST_CMD tests/test_orders.py"
        ;;
    "companies")
        PYTEST_CMD="$PYTEST_CMD tests/test_companies.py"
        ;;
    *)
        echo -e "${RED}Error: Invalid test type '$TEST_TYPE'${NC}"
        echo "Valid types: all, unit, integration, auth, products, orders, companies"
        exit 1
        ;;
esac

# Add markers if specified
if [[ -n "$MARKERS" ]]; then
    PYTEST_CMD="$PYTEST_CMD -m $MARKERS"
fi

# Add coverage options
if [[ "$COVERAGE" == true ]]; then
    PYTEST_CMD="$PYTEST_CMD --cov=tigu_backend_fastapi/app"
    PYTEST_CMD="$PYTEST_CMD --cov-report=term-missing"
    PYTEST_CMD="$PYTEST_CMD --cov-report=html:$OUTPUT_DIR/htmlcov"
    PYTEST_CMD="$PYTEST_CMD --cov-report=xml:$OUTPUT_DIR/coverage.xml"
    PYTEST_CMD="$PYTEST_CMD --cov-fail-under=70"
fi

# Add verbose option
if [[ "$VERBOSE" == true ]]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add parallel option
if [[ "$PARALLEL" == true ]]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

# Add fail fast option
if [[ "$FAIL_FAST" == true ]]; then
    PYTEST_CMD="$PYTEST_CMD -x"
fi

# Add output options
PYTEST_CMD="$PYTEST_CMD --junitxml=$OUTPUT_DIR/junit.xml"
PYTEST_CMD="$PYTEST_CMD --tb=short"

# Print configuration
echo -e "${BLUE}API Test Runner Configuration:${NC}"
echo -e "Test Type: ${YELLOW}$TEST_TYPE${NC}"
echo -e "Coverage: ${YELLOW}$COVERAGE${NC}"
echo -e "Verbose: ${YELLOW}$VERBOSE${NC}"
echo -e "Parallel: ${YELLOW}$PARALLEL${NC}"
echo -e "Fail Fast: ${YELLOW}$FAIL_FAST${NC}"
echo -e "Output Directory: ${YELLOW}$OUTPUT_DIR${NC}"
if [[ -n "$MARKERS" ]]; then
    echo -e "Markers: ${YELLOW}$MARKERS${NC}"
fi
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: No virtual environment detected. Consider activating one.${NC}"
    echo ""
fi

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
python -m pip list | grep -E "(pytest|fastapi|sqlalchemy)" > /dev/null || {
    echo -e "${RED}Error: Required dependencies not found. Run: pip install -r requirements.txt${NC}"
    exit 1
}
echo -e "${GREEN}Dependencies OK${NC}"
echo ""

# Set environment variables for testing
export TESTING=true
export DATABASE_URL="sqlite:///./test.db"

# Run tests
echo -e "${BLUE}Running tests...${NC}"
echo -e "${YELLOW}Command: $PYTEST_CMD${NC}"
echo ""

# Execute the pytest command
if eval $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}✅ Tests completed successfully!${NC}"
    
    # Show coverage summary if enabled
    if [[ "$COVERAGE" == true ]]; then
        echo ""
        echo -e "${BLUE}📊 Coverage Report:${NC}"
        echo -e "HTML Report: ${YELLOW}$OUTPUT_DIR/htmlcov/index.html${NC}"
        echo -e "XML Report: ${YELLOW}$OUTPUT_DIR/coverage.xml${NC}"
    fi
    
    # Show JUnit report
    echo -e "JUnit Report: ${YELLOW}$OUTPUT_DIR/junit.xml${NC}"
    
    exit 0
else
    echo ""
    echo -e "${RED}❌ Tests failed!${NC}"
    echo -e "Check the output above for details."
    echo -e "Reports saved to: ${YELLOW}$OUTPUT_DIR/${NC}"
    exit 1
fi 