function gcm
  echo "$(git diff HEAD | sed 1,2d)" | lm -t commit --no-context $argv
end
