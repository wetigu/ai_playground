# GitHub Actions Local Testing with `act` - Troubleshooting Guide

## Issue: Upload Artifacts Failure

When running GitHub Actions locally with `act`, you may encounter this error:

```
❗  ::error::Unable to get the ACTIONS_RUNTIME_TOKEN env variable
❌  Failure - Main Upload build artifacts
```

## Root Cause

The `actions/upload-artifact@v4` action requires the `ACTIONS_RUNTIME_TOKEN` environment variable, which is automatically provided by GitHub's runtime environment but is not available when running locally with `act`.

## Solution: Conditional Artifact Upload

Add a condition to skip upload-artifact steps when running locally with `act`:

### ✅ **Fixed Workflow:**

```yaml
- name: Upload build artifacts
  # Skip this step when running locally with act
  if: ${{ !env.ACT }}
  uses: actions/upload-artifact@v4
  with:
    name: dist-files-${{ matrix.node-version }}
    path: tigu_frontend_vue/dist/
    retention-days: 7
```

### 🔧 **For Conditional Uploads (e.g., on failure):**

```yaml
- name: Upload Cypress screenshots
  uses: actions/upload-artifact@v4
  # Skip when running locally with act, only run on GitHub
  if: failure() && !env.ACT
  with:
    name: cypress-screenshots
    path: tigu_frontend_vue/cypress/screenshots/
```

## How It Works

- `env.ACT` is an environment variable that is automatically set to `true` when running with `act`
- `!env.ACT` evaluates to `false` when running locally, so the step is skipped
- On GitHub's runners, `env.ACT` is not set (evaluates to falsy), so `!env.ACT` is `true` and the step runs

## Alternative Solutions

### 1. **Use act with artifact server simulation**
```bash
# Run with artifact server (limited functionality)
act --artifact-server-path ./artifacts
```

### 2. **Mock the upload step**
```yaml
- name: Upload build artifacts (local mock)
  if: env.ACT
  run: |
    echo "📦 Would upload artifacts: tigu_frontend_vue/dist/"
    echo "Files that would be uploaded:"
    find tigu_frontend_vue/dist/ -type f | head -10
```

### 3. **Skip upload entirely for local testing**
```bash
# Run specific job without upload steps
act -j test --skip-steps="Upload build artifacts"
```

## Testing Your Fix

1. **Run the workflow locally:**
   ```bash
   act -j test
   ```

2. **Verify the step is skipped:**
   - Look for missing "Upload build artifacts" in the output
   - The workflow should complete successfully

3. **Test on GitHub:**
   - Push changes to GitHub
   - Verify artifacts are uploaded in the real environment

## Benefits of This Approach

✅ **Works locally with act**
✅ **Works on GitHub Actions**  
✅ **No functionality loss on GitHub**
✅ **Clear intent with comments**
✅ **Maintains artifact functionality for CI/CD**

## Other Common `act` Issues

### Missing Secrets
```bash
# Create .secrets file
echo "MY_SECRET=test-value" > .secrets
act --secret-file .secrets
```

### Network Access Issues
```bash
# Use host network mode
act --container-daemon-socket /var/run/docker.sock
```

### Container Platform Issues
```bash
# Specify platform for different architectures  
act -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

## Conclusion

The `if: ${{ !env.ACT }}` condition is the cleanest solution for handling upload-artifact incompatibilities with `act`. It allows you to test your CI/CD pipeline locally while maintaining full functionality on GitHub Actions. 