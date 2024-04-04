# Convert date and time to timestamp format
datetime_to_timestamp() {
        date -d "$1 $2" +%s
}

# Convert timestamp to date and hour
timestamp_to_datehour() {
        date -d @$1 "+%Y-%m-%d_%H"
}

# Convert timestamp to date and time (format: %Y-%m-%d_%H.%M.%S)
timestamp_to_datetime_dot() {
        date -d @$1 "+%Y-%m-%d_%H.%M.%S"
}

# Convert timestamp to date and time (format: %Y-%m-%d_%H:%M:%S)
timestamp_to_datetime() {
        date -d @$1 "+%Y-%m-%d_%H:%M:%S"
}

create_x_range() {
    local x0=$1
    local xf=$2
    local dx=$3
    local -a x_array=()
    local x=$x0
    while (( $x <= $xf )); do
	x_array+=("$x")
	x=$(($x + $dx))
    done

    echo "${x_array[@]}"
}

create_datetime_dot_range() {
    local date_initial="$1"
    local time_initial="$2"
    local date_final="$3"
    local time_final="$4"
    local dt="$5"

    # Convert initial and final datetimes to timestamps
    local timestamp_initial=$(datetime_to_timestamp "$date_initial" "$time_initial")
    local timestamp_final=$(datetime_to_timestamp "$date_final" "$time_final")

    # Initialize an empty array for date and hour
    local -a datehour_array=()

    # Loop through timestamps and append corresponding dates to the array
    local current_timestamp=$timestamp_initial
    while [ "$current_timestamp" -le "$timestamp_final" ]; do
        local current_date=$(timestamp_to_datetime_dot "$current_timestamp")
        date_array+=("$current_date")
        current_timestamp=$((current_timestamp + $dt)) # Add dt (in seconds)
    done

    # Return the array containing the dates
    echo "${date_array[@]}"
}

create_datetime_range() {
    local date_initial="$1"
    local time_initial="$2"
    local date_final="$3"
    local time_final="$4"
    local dt="$5"

    # Convert initial and final datetimes to timestamps
    local timestamp_initial=$(datetime_to_timestamp "$date_initial" "$time_initial")
    local timestamp_final=$(datetime_to_timestamp "$date_final" "$time_final")

    # Initialize an empty array for date and hour
    local -a datehour_array=()

    # Loop through timestamps and append corresponding dates to the array
    local current_timestamp=$timestamp_initial
    while [ "$current_timestamp" -le "$timestamp_final" ]; do
        local current_date=$(timestamp_to_datetime "$current_timestamp")
        date_array+=("$current_date")
        current_timestamp=$((current_timestamp + $dt)) # Add dt (in seconds)
    done

    # Return the array containing the dates
    echo "${date_array[@]}"
}

create_datehour_range() {
    local date_initial="$1"
    local time_initial="$2"
    local date_final="$3"
    local time_final="$4"
    local dt="$5"

    # Convert initial and final datetimes to timestamps
    local timestamp_initial=$(datetime_to_timestamp "$date_initial" "$time_initial")
    local timestamp_final=$(datetime_to_timestamp "$date_final" "$time_final")

    # Initialize an empty array for date and hour
    local -a datehour_array=()

    # Loop through timestamps and append corresponding dates to the array
    local current_timestamp=$timestamp_initial
    while [ "$current_timestamp" -le "$timestamp_final" ]; do
        local current_date=$(timestamp_to_datehour "$current_timestamp")
        date_array+=("$current_date")
	current_timestamp=$((current_timestamp + $dt)) # Add dt (in seconds)
    done

    # Return the array containing the dates
    echo "${date_array[@]}"
}


# Modify value of a specific parameter in text file
modify_param_value() {
    local input_file="$1"
    local param="$2"
    local value="$3"

    # Function to perform substitution
    substitute_value() {
        local line="$1"
        local key="${line%%=*}"
        local new_line="$key=$value"
        echo "$new_line"
    }

    # Check if input file exists
    if [ ! -f "$input_file" ]; then
        echo "Error: Input file '$input_file' not found."
        return 1
    fi

    local tmp_file="$(mktemp)"
    # Process input file
    while IFS= read -r line; do
        if [[ $line == "$param="* ]]; then
            # Line contains the specified parameter: perform substitution
            new_line=$(substitute_value "$line")
            echo "$new_line" >> "$tmp_file"
        else
            # Line does not match the specified variable, keep as is
            echo "$line" >> "$tmp_file"
        fi
    done < "$input_file"

    # Replace original file with modified file
    mv "$tmp_file" "$input_file"
}

# Testing create_datehour_range
#date1=2017-04-03
#time1=18:00:00
#date2=2017-04-05
#time2=00:00:00
#date_array=($(create_datehour_range $date1 $time1 $date2 $time2 3600))
#for DATEHOUR in "${date_array[@]}"; do
#    echo $DATEHOUR
#done
