""" Equation formatter for Mathematica.
"""

# Imports: User
from .equation_formatter import EquationFormatter


class MathematicaFormatter(EquationFormatter):
    """ A static class that contains equation formatting functions that are
        generated by the equation generator.
    """

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # Public Interface.
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    # --------------------------------------------------------------------------
    # CONSTANTS.
    # --------------------------------------------------------------------------

    @staticmethod
    def get_constraint(constraint):
        """ Gets the string that represents a constraint of the system in
            Mathematica format.

            :param constraint: The variable that contains the constraint, in
            the form of equalities.

            :return constraint_string: The string that represents the constraint
            in Mathematica format.
        """

        # ----------------------------------------------------------------------
        # Auxiliary functions.
        # ----------------------------------------------------------------------

        # Get the lowest order state.
        low_state_string = MathematicaFormatter.get_state(constraint[0])

        # Define it as a mathematica function.
        low_state_string = "".join(low_state_string.split("[t]")) + "[t_]"

        # Get the other states.
        other_states = list(map(MathematicaFormatter.get_state, constraint[1]))

        # Join the states.
        other_states = " + ".join(other_states)

        # Join the strings.
        constraint_string = low_state_string + " := " + other_states

        return constraint_string

    @staticmethod
    def get_equation(equation, order=0):
        """ Gets the string that represents an equation from a Master Equation
            in Mathematica format.

            :param equation: The variable that contains the state and its
            constituents for which to get the equation.

            :param order: The order to which the state must be expanded. Order
            zero means the state must not be modified. Higher orders means the
            state must be mean-field expanded to the given order.

            :return equation_string: The string that represents the Master
            Equation in Mathematica format.
        """

        # ----------------------------------------------------------------------
        # Auxiliary functions.
        # ----------------------------------------------------------------------

        def format_create_decay(key0, create_states0, decay_states0):
            """ Given the decay states and the key, it formats the string of
                decay states.

                :param key0: The key that is being formatted.

                :param create_states0: The create states associated with the
                key.

                :param decay_states0: The decay states associated with the key.

                :return create_decay_string0: The string that represents the
                specific term in the equation.
            """

            # Get the string representation of the key.
            string_key = MathematicaFormatter.get_rate(key0)

            # Join the states in the create states list.
            create_string0 = "+".join(create_states0)

            # Join the states in the decay states list.
            decay_string0 = "-" + "-".join(decay_states0)

            # Join the strings.
            create_decay_string0 = f"+{string_key} (" + create_string0 + decay_string0 + f")"

            return create_decay_string0

        def format_create_decay_single(key0, states0, decay=False):
            """ Given the decay states and the key, it formats the string of
                decay states.

                :param key0: The key that is being formatted.

                :param states0: The create/decay states associated with the key.

                :param decay: True, if the requested states to be added are
                decay states. False, otherwise, i.e., create states.

                :return create_decay_string: The string that represents the
                specific term in the equation.
            """

            # ------------------------------------------------------------------
            # Auxiliary functions.
            # ------------------------------------------------------------------

            def get_prefactor(state_string1):
                """ Given a state string, it returns the string of the numerical
                    coefficient, and the stripped state.
                """

                # Auxiliary variables.
                j = 0
                tmp_string1 = ""

                # Every character in the string.
                for character in state_string1:
                    # If the character is not a number.
                    if not str.isnumeric(character):
                        break

                    # Add the character to the string.
                    tmp_string1 += character

                    # Add one to the counter.
                    j += 1

                # Format the string properly.
                state_string1 = state_string1[j:] if j < len(state_string1) else state_string1

                # THIS SHOULD NOT HAPPEN!
                return tmp_string1, state_string1

            # ------------------------------------------------------------------
            # Implementation.
            # ------------------------------------------------------------------

            # Get the string representation of the key.
            string_key = MathematicaFormatter.get_rate(key0)

            # Initialize the string and the negative sign as needed.
            create_decay_string0 = "-" if decay else "+"

            # If there is only one state.
            if len(states0) == 1:
                # Get the prefactor and state.
                prefactor0, create_decay_string0_0 = get_prefactor(states0[0])

                # Join the string.
                create_decay_string0 += f"{prefactor0} {string_key} {create_decay_string0_0}"

            else:
                # Join the states.
                create_decay_string0 += f"{string_key} (" + "+".join(states0) + ")"

            return create_decay_string0

        def format_equation_string(equation_string0):
            """ Formats the equation string further to include spaces for
                readability.

                :param equation_string0: The string to be formatted.

                :return equation_string0_0: The properly formatted string.
            """

            # Strip all the leading and trailing spaces.
            equation_string0_0 = equation_string0.strip()

            # Save the negative character if needed.
            first_character0 = "-" if equation_string0[0] == "-" else ""

            # Determine if there is a positive or negative sign at the start.
            delete_first0 = equation_string0_0[0] == "-" or equation_string0_0[0] == "+"
            equation_string0_0 = equation_string0_0[1:] if delete_first0 else equation_string0_0

            # Strip all the leading and trailing spaces, again.
            equation_string0_0 = equation_string0_0.strip()

            # Space the positive and negative signs correctly.
            equation_string0_0 = " + ".join(equation_string0_0.split("+"))
            equation_string0_0 = " - ".join(equation_string0_0.split("-"))

            # Add the first character.
            equation_string0_0 = first_character0 + equation_string0_0

            return equation_string0_0

        def format_state_multiplicity(state0):
            """ Returns the state string, properly formatted, multiplied by its
                multiplicity.

                :param state0: A 2-tuple of the state with its multiplicity.

                :return: The state string, properly formatted, multiplied by its
                multiplicity
            """

            # Check that the state is an iterable of length 2.
            if not len(state0) == 2:
                raise ValueError("To properly format the state it must be a"
                                 " tuple of lenght 2.")

            # Get the multiplicity.
            state0_0 = str(state0[1]) if state0[1] > 1 else ""

            # Get the state representation.
            state0_0 += MathematicaFormatter.get_state(state0[0], order)

            return state0_0

        def validate_equation():
            """ Validates that the equation is given in the proper format.
                    (state, create states dictonary, decay states dictionary)
            """

            # Check that the equation is tuple.
            if not isinstance(equation, (tuple,)):
                raise TypeError(f"The equation must be a tuple. Current type: {type(equation)}.")

            # Of length 3.
            elif not len(equation) == 3:
                raise TypeError(f"The equation must be a tuple of three entries."
                                f" Current type: {type(equation)}, Length = {len(equation)}"
                                )

            # Validate that the zeroth entry is a state.
            validate_state(equation[0])

            # Validate that the first and second entries are dictionaries.
            if not (isinstance(equation[1], (dict,)) and isinstance(equation[2], (dict,))):
                raise TypeError("The two last entries of the tuple must be dictionaries. "
                                f" Dictionary entry [1] = {type(equation[1])},"
                                f" Dictionary entry [2] = {type(equation[2])}."
                                )

            # Get the keys to the dictionaries.
            keys0_1 = set(key0 for key0 in equation[1].keys())
            keys0_2 = set(key0 for key0 in equation[2].keys())

            # If their keys are different.
            if not keys0_1 == keys0_2:
                raise ValueError(f"Both Dictionaries must have the same keys"
                                 f" Keys for equation[1]: {keys0_1},"
                                 f" Keys for equation[2]: {keys0_2}.")

        def validate_state(state0):
            """ Validates that the state is given in the proper format.

                :param state0: A state that must be in the format,
                    ((particle0, index0), ... ,(particleN, indexN),).
            """

            # Check that it is a tuple.
            if not isinstance(state0, (tuple,)):
                raise TypeError(f"The state parameter must be a tuple. Current type: {type(state0)}")

            # Check that the elements are tuples.
            for j0, substate0 in enumerate(state0):
                # Check that it is a tuple.
                if not isinstance(substate0, (tuple,)):
                    raise TypeError(f"The substates of a state must be tuple."
                                    f" State = {state0}, Substate Entry = {j0},"
                                    f" Substate = {substate0}, Current type: {type(substate0)}"
                                    )

                # Of length 2.
                elif not len(substate0) == 2:
                    raise TypeError(f"The substates of a state must be tuple of length 2. "
                                    f" State = {state0}, Substate Entry = {j0},"
                                    f" Substate = {substate0},  Current length of substate: {len(substate0)}."
                                    )

        # ----------------------------------------------------------------------
        # Implementation.
        # ----------------------------------------------------------------------

        # Validate the equation.
        validate_equation()

        # Auxiliary variables.
        keys = tuple(key for key in equation[1].keys())

        # Get the differential form.
        diff_state = "D[" + MathematicaFormatter.get_state(equation[0]) + ", t] == "

        # The string where the equation will be stored.
        equation_string = ""

        # For every key.
        for key in keys:
            # Get the create states representations.
            create_states = [format_state_multiplicity(state) for state in equation[1][key]]

            # Get the decay states representations.
            decay_states = [format_state_multiplicity(state) for state in equation[2][key]]

            # If there are decay states but no creation states.
            if len(decay_states) > 0 and len(create_states) == 0:
                # Get the decay string.
                decay_string = format_create_decay_single(key, decay_states, decay=True)

                # Add to the equation string.
                equation_string += decay_string

            # If there are no decay states, but there are creation states.
            elif len(decay_states) == 0 and len(create_states) > 0:
                # Get the create string.
                create_string = format_create_decay_single(key, create_states, decay=False)

                # Add to the equation string.
                equation_string += create_string

            # If there are both decay states and creation states.
            elif len(decay_states) > 0 and len(create_states) > 0:
                # Get the decay and create string.
                create_decay_string = format_create_decay(key, create_states, decay_states)

                # Add to the equation string.
                equation_string += create_decay_string

        # Format the string properly.
        equation_string = format_equation_string(equation_string)

        # Join the strings.
        equation_string = diff_state + equation_string

        return equation_string

    @staticmethod
    def get_initial_condition(state, time=0, value=0):
        """ Gets the string that represents a state equal to a given initial
            condition that, by default, is set to zero.

            :param state: The state whose initial condition will be.

            :param time: A parameter, that must allow a string reprsentation,
            that denotes the time of the initial condition. Set to zero by
            default.

            :param value: The value of the initial condition. Must allow a
            string representation.

            :return constraint_string: The string that represents the initial
            condition of a state.
        """
        # Remove the time dependency.
        initial_condition_string = "".join(MathematicaFormatter.get_state(state).split("[t]")[:-1])

        # Add the initial condition.
        initial_condition_string += f"[{str(time)}] == {str(value)}"

        return initial_condition_string

    @staticmethod
    def get_rate(rate):
        """ Gets the string that represents a rate constant in Mathematica format.

            :param rate: The rate to check. If in the format,
                 "'s1'.'s2'. ... .'sN'.."
            it interprets the periods as sub-indexes of level N.

            :return rate_string: The rate constant in the given representation.
        """

        # ----------------------------------------------------------------------
        # Auxiliary functions.
        # ----------------------------------------------------------------------

        def validate_rate():
            """ Validates that the rate is given in the proper format.

                :param rate: The rate to check. If in the format,
                     "'s1'.'s2'. ... .'sN'.."
                it interprets the periods as sub-indexes of level N.
            """

            # Check that it is a string.
            if not isinstance(rate, (str,)):
                raise TypeError(f"The rate parameter must be string. Current type: {type(rate)}")

        # ----------------------------------------------------------------------
        # Implementation.
        # ----------------------------------------------------------------------

        # Validate the form of the rate.
        validate_rate()

        # Split the string.
        rate_string = rate.split(".")

        # Join the string properly, in all upper case.
        rate_string = "".join(rate_string).upper()

        return rate_string

    @staticmethod
    def get_rate_value(rate, value=0):
        """ Gets the string that represents a rate constant in Mathematica
            format, with the given value.

            :param rate: The rate to check. If in the format,
                 "'s1'.'s2'. ... .'sN'.."
            it interprets the periods as sub-indexes of level N.

            :param value: The value of the rate. Set to zero as default.

            :return rate_string: The rate constant in Mathematica format.
        """

        # Get the rate representation.
        rate_string = MathematicaFormatter.get_rate(rate)

        # Set the value.
        rate_string += f" = {value}"

        return rate_string

    @staticmethod
    def get_state(state, order=0):
        """ Gets the string that represents a state in Mathematica format.

            :param state: A state in the format,
                ((particle0, index0), ... ,(particleN, indexN),).

            :param order: The order to which the state must be approximated.
            If zero, the state is NOT approximated.

            :return state_string: The state, to the given order, in Mathematica
            format.
        """

        # ----------------------------------------------------------------------
        # Auxiliary functions.
        # ----------------------------------------------------------------------

        def format_entry(entry0):
            """ Formats an entry of a state properly.

                :param entry0: The entry to be formatted.

                :return entry_string0: The entry of a state in string format.
            """

            entry_string0 = f"{entry0[0]}{entry0[1]}"

            return entry_string0

        def get_denominator():
            """ Gets the denominator for the equations. This is obtained from
                the numerator.

                :return: The list of states that is generated from the
                numerator, that will go in the denominator.
            """

            # Auxiliary variables.
            state_list0 = []

            # For every ith state.
            for i, state0_0 in enumerate(numerator_states):
                # For every jth state.
                for j, state0_1 in enumerate(numerator_states):
                    # The denominator will be the intersection of the states.
                    if j <= i:
                        continue

                    # Get the intersecting states.
                    intersecting_states0 = list(set(state0_0).intersection(set(state0_1)))

                    # If there are intersecting states.
                    if len(intersecting_states0) > 0:
                        # Extend the list if there is intersection.
                        state_list0.append(intersecting_states0)

            return state_list0

        def get_numerator():
            """ Gets the split state to the nth order, using a mean-field
                approximation.

                :return: A list of the states that is generated from an nth
                order mean field approximation.
            """

            # Auxiliary variables.
            state_list0 = []

            # For every index in the state.
            for i, _ in enumerate(state):
                # Cannot generate more states.
                if i + order > len(state):
                    break

                # Append the substate.
                state_list0.append(state[i: i + order])

            return state_list0

        def get_state_string(state0):
            """ Given a state it returns the string representation.

                :param state0: A tuple of two-tuples.

                :return state_string0_0: The CLOSED reprensentation of a state.
            """

            # Get the list of entries.
            entries0 = list(map(format_entry, state0))

            # Get the exact representation of the state.
            state_string0_0 = "P" + "".join(entries0) + "[t]"

            return state_string0_0

        def validate_state():
            """ Validates that the state is given in the proper format.
            """

            # The order must a number greater than zero.
            if not 0 <= order:
                raise ValueError(f"The order must be a positive value. Current Value {order}.")

            # Check that it is a tuple.
            if not isinstance(state, (tuple,)):
                raise TypeError(f"The state parameter must be a tuple. Current type: {type(state)}")

            # Check that the elements are tuples.
            for j, substate in enumerate(state):
                # Check that it is a tuple.
                if not isinstance(substate, (tuple,)):
                    raise TypeError(f"The substates of a state must be tuple."
                                    f" State = {state}, Substate Entry = {j},"
                                    f" Substate = {substate}, Current type: {type(substate)}"
                                    )

                # Of length 2.
                elif not len(substate) == 2:
                    raise TypeError(f"The substates of a state must be tuple of length 2. "
                                    f" State = {state}, Substate Entry = {j},"
                                    f" Substate = {substate},  Current length of substate: {len(substate)}."
                                    )

        # ----------------------------------------------------------------------
        # Implementation.
        # ----------------------------------------------------------------------

        # Always validate the state.
        validate_state()

        # If the requested order is zero.
        if order == 0 or order >= len(state):
            # Get the string representation of the state.
            state_string = get_state_string(state)

            return state_string

        # Split the state in the requested order.
        numerator_states = get_numerator()

        # Get the denominator states.
        denominator_states = get_denominator()

        # ----------------------------------------------------------------------
        # Get the strings for the numerator and denominator.
        # ----------------------------------------------------------------------

        # Strings for the numerator states.
        numerator_states = list(map(get_state_string, numerator_states))

        # Format the string.
        state_string = " ".join(numerator_states)

        # Get the denominator strings.
        if len(denominator_states) > 0:
            # Strings for the denominator states.
            denominator_states = list(map(get_state_string, denominator_states))

            # Format the string.
            state_string = state_string + "/(" + " ".join(denominator_states) + ")"

        return state_string

    @staticmethod
    def get_state_raw(state):
        """ Gets the string that represents a 'raw state' in Mathematica format.

            :param state: A state in the format,
                ((particle0, index0), ... ,(particleN, indexN),).

            :return state_string: The state, to the given order, in Mathematica
            format. In some cases, the raw format might be the same as the
            regular format.
        """

        # Get the state.
        state_string = MathematicaFormatter.get_state(state)

        # Take the time dependence off and strip the state from leading/trailing spaces.
        state_string = "".join(state_string.split("[t]")).strip()

        return state_string

    # --------------------------------------------------------------------------
    # Other Formatting Functions.
    # --------------------------------------------------------------------------

    @staticmethod
    def join_equations(quantities):
        """ Formats the equations and the different quantities such that it
            ready to be saved in a string.

            :param quantities: A dictionary that MUST have the following
            format, with the keys AS SHOWN

                - "constraints": A list of strings of constraints.
                - "equations": A list of strings of the equations.
                - "initial conditions": A list of the strings of the initial
                  conditions.
                - "rate values": A list of the strings with the values of the
                  constants.
                - "raw_states": A list with the representation of the raw
                  states. For some formats the raw states may be the same as the
                  regular states.

            :return formatted_system: A single string of the formatted equations.
        """

        # ----------------------------------------------------------------------
        # Auxiliary functions.
        # ----------------------------------------------------------------------

        def format_equations():
            """ Formats the equations properly.

                :return:
            """
            # TODO: Finish this and everything will be done, add this function to the formatter_latex.py file.

            equations_list = ",\n\t".join(quantities["equations"]) + "\t" + ",\n\t".join(
                quantities["initial conditions"])
            equations_list = equations_list[:-1] if equations_list[-1] == "\n" else equations_list
            equations_list = "equations = {\n\t" + equations_list + "\n}"

        def validate_dictionary(keys0):
            """ Validates that the dictionary is consistent.
            """

            # Get ALL the keys.
            keys0_0 = [key0_1 for key0_1 in quantities.keys()]

            # Validate that it is a dictionary.
            if not isinstance(quantities, (dict,)):
                raise TypeError("The quantities parameter must be a dictionary.")

            # Validate the entries.
            if not set(keys0_0) == set(keys0):
                raise ValueError(f"The keys in the dictionary must be {keys0}."
                                 f" Current keys = {keys0_0}.")

        # ----------------------------------------------------------------------
        # Implementation.
        # ----------------------------------------------------------------------

        # Dictionary keys are.
        keys = ["constraints", "equations", "initial conditions", "rate values", "raw states"]

        # Always validate first.
        validate_dictionary(keys)

        # Join the equations and initial conditions.
        equations_list = format_equations()

