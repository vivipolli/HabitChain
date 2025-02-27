import { motion, useMotionValue, useTransform } from "framer-motion";

const tickVariants = {
    pressed: (isChecked) => ({ pathLength: isChecked ? 0.85 : 0.2 }),
    checked: { pathLength: 1 },
    unchecked: { pathLength: 0 }
};

const boxVariants = {
    hover: { scale: 1.05, strokeWidth: 3 },
    pressed: { scale: 0.95, strokeWidth: 2 },
    checked: { stroke: "#0EA5E9" },
    unchecked: { stroke: "#BAE6FD", strokeWidth: 2 }
};

export const Example = ({ isChecked, onCheck }) => {
    const pathLength = useMotionValue(0);
    const opacity = useTransform(pathLength, [0.05, 0.15], [0, 1]);

    return (
        <motion.svg
            initial={false}
            animate={isChecked ? "checked" : "unchecked"}
            whileHover="hover"
            whileTap="pressed"
            width="28"
            height="28"
            onClick={onCheck}
            className="cursor-pointer"
        >
            <motion.path
                d="M 5 9 C 5 6.79086 6.79086 5 9 5 L 19 5 C 21.2091 5 23 6.79086 23 9 L 23 19 C 23 21.2091 21.2091 23 19 23 L 9 23 C 6.79086 23 5 21.2091 5 19 Z"
                fill="transparent"
                strokeWidth="2"
                stroke="#BAE6FD"
                variants={boxVariants}
            />
            <motion.path
                d="M 8 14 L 12 18 L 20 9"
                transform="translate(0, 0) rotate(0)"
                fill="transparent"
                strokeWidth="3"
                stroke="#3cfb46"
                strokeLinecap="round"
                strokeLinejoin="round"
                variants={tickVariants}
                style={{ pathLength, opacity }}
                custom={isChecked}
            />
        </motion.svg>
    );
};
