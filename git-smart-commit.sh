#!/bin/bash

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show git status with colors
show_git_status() {
    echo -e "${BLUE}Current Git Status:${NC}"
    git status --short
}

# Function to show changed files
show_changed_files() {
    echo -e "${BLUE}Changed Files:${NC}"
    git diff --name-only
}

# Function to push changes
push_changes() {
    echo -e "${BLUE}Pushing changes to remote...${NC}"
    
    # Get current branch
    current_branch=$(git branch --show-current)
    
    echo -e "Current branch: ${GREEN}$current_branch${NC}"
    echo -e "${YELLOW}Select push option:${NC}"
    echo "1) Push to origin/$current_branch"
    echo "2) Push to a different remote/branch"
    echo "3) Cancel"
    read -p "Choose an option: " push_choice
    
    case $push_choice in
        1)
            echo -e "${BLUE}Pushing to origin/$current_branch...${NC}"
            if git push origin $current_branch; then
                echo -e "${GREEN}Successfully pushed to origin/$current_branch${NC}"
            else
                echo -e "${RED}Failed to push to origin/$current_branch${NC}"
            fi
            ;;
        2)
            read -p "Enter remote name [origin]: " remote_name
            remote_name=${remote_name:-origin}
            read -p "Enter branch name [$current_branch]: " branch_name
            branch_name=${branch_name:-$current_branch}
            
            echo -e "${BLUE}Pushing to $remote_name/$branch_name...${NC}"
            if git push $remote_name $branch_name; then
                echo -e "${GREEN}Successfully pushed to $remote_name/$branch_name${NC}"
            else
                echo -e "${RED}Failed to push to $remote_name/$branch_name${NC}"
            fi
            ;;
        *)
            echo -e "${YELLOW}Push cancelled${NC}"
            ;;
    esac
}

# Function to analyze file changes and generate description
analyze_changes() {
    local files_changed=$(git diff --name-only)
    local diff_content=$(git diff)
    local description=""
    local scope=""
    
    # Analyze Python files for function/class changes
    if echo "$diff_content" | grep -q "^+.*class.*:"; then
        local classes=$(echo "$diff_content" | grep "^+.*class.*:" | sed 's/^+.*class \([^(:]*\).*/\1/')
        description+="add classes: $classes; "
    fi
    
    if echo "$diff_content" | grep -q "^+.*def.*:"; then
        local functions=$(echo "$diff_content" | grep "^+.*def.*:" | sed 's/^+.*def \([^(:]*\).*/\1/')
        description+="add functions: $functions; "
    fi
    
    # Detect authentication-related changes
    if echo "$diff_content" | grep -qi "auth\|login\|session"; then
        scope="auth"
        if echo "$diff_content" | grep -qi "digest"; then
            description+="implement digest authentication; "
        fi
        if echo "$diff_content" | grep -qi "sha.*256"; then
            description+="add SHA-256 support; "
        fi
    fi
    
    # Detect API-related changes
    if echo "$files_changed" | grep -qi "api"; then
        if [ -z "$scope" ]; then
            scope="api"
        fi
        if echo "$diff_content" | grep -qi "endpoint\|route"; then
            description+="add API endpoints; "
        fi
    fi
    
    # Detect configuration changes
    if echo "$files_changed" | grep -qi "config\|settings\|env"; then
        if [ -z "$scope" ]; then
            scope="config"
        fi
        description+="update configuration; "
    fi
    
    # Detect test additions
    if echo "$files_changed" | grep -q "test"; then
        if [ -z "$scope" ]; then
            scope="test"
        fi
        description+="add tests; "
    fi
    
    # Detect documentation updates
    if echo "$files_changed" | grep -qi "\.md\|docs"; then
        if [ -z "$scope" ]; then
            scope="docs"
        fi
        description+="update documentation; "
    fi
    
    # Remove trailing semicolon and space
    description=$(echo "$description" | sed 's/; $//')
    
    echo "SCOPE:$scope"
    echo "DESC:$description"
}

# Function to detect breaking changes
detect_breaking_changes() {
    local diff_content=$(git diff)
    local breaking_changes=""
    
    # Check for function signature changes
    if echo "$diff_content" | grep -q "^-.*def.*:.*$"; then
        breaking_changes+="modified function signatures; "
    fi
    
    # Check for removed classes
    if echo "$diff_content" | grep -q "^-.*class.*:.*$"; then
        breaking_changes+="removed/modified classes; "
    fi
    
    # Check for configuration changes
    if echo "$diff_content" | grep -qi "^-.*\(API_KEY\|SECRET\|PASSWORD\|CONFIG\).*$"; then
        breaking_changes+="modified critical configuration; "
    fi
    
    # Check for database schema changes
    if echo "$diff_content" | grep -qi "^-.*\(CREATE TABLE\|ALTER TABLE\|DROP TABLE\).*$"; then
        breaking_changes+="modified database schema; "
    fi
    
    echo "$breaking_changes"
}

# Function to generate commit type suggestions based on changed files
suggest_commit_type() {
    local files_changed=$(git diff --name-only)
    local diff_content=$(git diff)
    
    # Check for new features
    if echo "$diff_content" | grep -q "^+.*\(class\|def\|function\).*:"; then
        echo "feat"
        return
    fi
    
    # Check for bug fixes
    if echo "$diff_content" | grep -qi "fix\|bug\|issue\|error\|crash"; then
        echo "fix"
        return
    fi
    
    # Check for tests
    if echo "$files_changed" | grep -q "test"; then
        echo "test"
        return
    fi
    
    # Check for documentation
    if echo "$files_changed" | grep -q "docs\|README\|\.md"; then
        echo "docs"
        return
    fi
    
    # Check for dependency updates
    if echo "$files_changed" | grep -q "package.json\|requirements.txt"; then
        echo "deps"
        return
    fi
    
    # Check for CI changes
    if echo "$files_changed" | grep -q "\.github\|\.gitlab\|\.circleci"; then
        echo "ci"
        return
    fi
    
    # Check for build system changes
    if echo "$files_changed" | grep -q "Dockerfile\|docker-compose"; then
        echo "build"
        return
    fi
    
    # Default to feat
    echo "feat"
}

# Function to show diff of each file
show_file_diffs() {
    echo -e "${BLUE}File Changes:${NC}"
    git diff --color
}

# Function to generate commit message template
generate_commit_template() {
    local commit_type=$(suggest_commit_type)
    local files_changed=$(git diff --name-only | tr '\n' ' ')
    
    echo -e "${YELLOW}Analyzing changes...${NC}"
    local analysis=$(analyze_changes)
    local scope=$(echo "$analysis" | grep "SCOPE:" | cut -d: -f2)
    local description=$(echo "$analysis" | grep "DESC:" | cut -d: -f2)
    
    local breaking_changes=$(detect_breaking_changes)
    
    echo -e "${YELLOW}Generated Commit Details:${NC}"
    echo -e "Type: ${GREEN}$commit_type${NC}"
    echo -e "Scope: ${GREEN}$scope${NC}"
    echo -e "Description: ${GREEN}$description${NC}"
    [ ! -z "$breaking_changes" ] && echo -e "Breaking Changes: ${RED}$breaking_changes${NC}"
    
    # Build commit message
    local commit_msg="$commit_type"
    if [ ! -z "$scope" ]; then
        commit_msg="$commit_msg($scope)"
    fi
    commit_msg="$commit_msg: $description"
    
    if [ ! -z "$breaking_changes" ]; then
        commit_msg="$commit_msg\n\nBREAKING CHANGE: $breaking_changes"
    fi
    
    echo -e "\n${BLUE}Generated Commit Message:${NC}"
    echo -e "$commit_msg"
    
    # Ask for confirmation or modification
    echo -e "\n${GREEN}Options:${NC}"
    echo "1) Use this message"
    echo "2) Modify the message"
    echo "3) Cancel"
    read -p "Choose an option: " choice
    
    case $choice in
        1)
            git commit -m "$commit_msg"
            echo -e "${GREEN}Changes committed successfully!${NC}"
            ;;
        2)
            echo -e "${GREEN}Enter your modified commit message:${NC}"
            read -e -i "$commit_msg" modified_msg
            git commit -m "$modified_msg"
            echo -e "${GREEN}Changes committed with modified message!${NC}"
            ;;
        *)
            echo -e "${YELLOW}Commit cancelled.${NC}"
            ;;
    esac
}

# Main menu
show_menu() {
    echo -e "${BLUE}=== Git Smart Commit Tool ===${NC}"
    echo -e "1) Show git status"
    echo -e "2) Show changed files"
    echo -e "3) Show detailed changes"
    echo -e "4) Stage all changes and commit"
    echo -e "5) Stage specific files and commit"
    echo -e "6) Push changes"
    echo -e "7) Exit"
    echo -e "${GREEN}Choose an option:${NC}"
}

# Main loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            show_git_status
            ;;
        2)
            show_changed_files
            ;;
        3)
            show_file_diffs
            ;;
        4)
            git add .
            generate_commit_template
            ;;
        5)
            show_git_status
            echo -e "${GREEN}Enter files to stage (space-separated):${NC}"
            read files
            git add $files
            generate_commit_template
            ;;
        6)
            push_changes
            ;;
        7)
            echo -e "${BLUE}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    
    echo -e "\nPress enter to continue..."
    read
    clear
done 