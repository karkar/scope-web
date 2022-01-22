import React, { ComponentType, createContext, FC, ReactElement, ReactNode, useContext } from 'react';
import { IPatientStore } from 'src/stores/PatientStore';
import { IRootStore } from 'src/stores/RootStore';

export const StoreContext = createContext<IRootStore | undefined>(undefined);

export type StoreComponent = FC<{
    store: IRootStore;
    children: ReactNode;
}>;

export const StoreProvider: StoreComponent = ({ children, store }): ReactElement => {
    return <StoreContext.Provider value={store}>{children}</StoreContext.Provider>;
};

export const useStores = () => useContext(StoreContext) as IRootStore;

export type TWithStoreHOC = <P extends unknown>(Component: ComponentType<P>) => (props: P) => JSX.Element;

// This pattern has typing issues. Use with caution
export const withStore: TWithStoreHOC = (WrappedComponent) => (props) => {
    const ComponentWithStore = () => {
        const store = useStores();

        return <WrappedComponent {...props} store={store} />;
    };

    ComponentWithStore.defaultProps = { ...WrappedComponent.defaultProps };
    ComponentWithStore.displayName = `WithStores(${WrappedComponent.name || WrappedComponent.displayName})`;

    // See https://reactjs.org/docs/higher-order-components.html#static-methods-must-be-copied-over
    // hoistNonReactStatics(ComponentWithStore, WrappedComponent);

    return <ComponentWithStore />;
};

export const PatientStoreContext = createContext<IPatientStore | undefined>(undefined);

export type PatientStoreComponent = FC<{
    patient: IPatientStore | undefined;
    children: ReactNode;
}>;

export const PatientStoreProvider: PatientStoreComponent = ({ children, patient }): ReactElement => {
    return <PatientStoreContext.Provider value={patient}>{children}</PatientStoreContext.Provider>;
};

export const usePatient = () => useContext(PatientStoreContext) as IPatientStore;
